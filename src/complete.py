
#This is GEMINI AI Functions ======

import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=api_key)
MODEL = "gemini-3.5-flash-lite"

 

def generate_question(role, experience, previous_evaluation, difficulty,previous_questions):

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=f"""
            You are an adaptive interview coach for {role} {experience}.

            Previous candidate performance:
            {previous_evaluation}
            Ask a question at the specified difficulty level: {difficulty}.
            Previous questions: {previous_questions}
            Do not repeat or rephrase them.

            Ask only one interview question and it should be 1 sentence (under 20 words).

            Follow these rules:
            - Match questions to the candidate's experience and skills.
            - Adjust difficulty gradually based on previous scores.
            - If the candidate struggles, ask an easier related question.
            - Avoid unrelated or repeated questions.
            - Never jump to advanced topics suddenly.
            """,
        )
        return response.text
    except APIError as e:
        print(f"Gemini API error: {e}")
        raise



def evaluate_answer(role, question, answer):
    try:
        evaluation = client.models.generate_content(
            model=MODEL,
            contents=f"""
            Role: {role}
            Interview question: {question}
            Candidate answer: {answer}

            Grade technical correctness and completeness.
            Ignore grammar unless code syntax is involved.

            Score from 0-10:
            0 = Incorrect
            1-3 = Major mistakes
            4-6 = Partially correct
            7-8 = Mostly correct
            9-10 = Fully correct

            Give short feedback.
            """,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "OBJECT",
                    "properties": {
                        "score": {"type": "INTEGER"},
                        "feedback": {"type": "STRING"},
                    },
                    "required": ["score", "feedback"],
                },
            },
        )
        data = json.loads(evaluation.text)
        return {"score": data["score"], "feedback": data["feedback"]}
    except APIError as e:
        print(f"Gemini API error: {e}")
        raise


def next_difficulty(difficulty, score):
    if score >= 8:
        if difficulty == "easy":
            return "medium"
        if difficulty == "medium":
            return "hard"
    elif score < 4:
        if difficulty == "hard":
            return "medium"
        if difficulty == "medium":
            return "easy"
    return difficulty


def final_summary(scores):
    if not scores:
        return {
            "average_score": 0,
            "message": "No scores available."
        }

    total = sum(item["score"] for item in scores)
    average_score = round(total / len(scores), 2)

    if average_score >= 8:
        message = "Excellent performance!"
    elif average_score >= 6:
        message = "Good performance. Keep improving."
    elif average_score >= 4:
        message = "Fair performance. More practice needed."
    else:
        message = "Needs improvement. Review the fundamentals."

    return {
        "average_score": average_score,
        "message": message
    }