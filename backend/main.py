
# THIS IS FAST API CODE ..

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.complete import (
    generate_question,
    evaluate_answer,
    next_difficulty,
    final_summary
)
import uuid
from google.genai.errors import APIError
from fastapi.responses import JSONResponse

app = FastAPI()
@app.exception_handler(APIError)
async def gemini_error_handler(request, exc):
    return JSONResponse(
        status_code=503,
        content={"detail": "AI service is temporarily unavailable. Please try again."}
    )
sessions = {}


@app.get("/")
def demo():
    return {"message": "hello world just demo"}


class StartRequest(BaseModel):
    role: str
    experience: str


@app.post("/interviews")
def interview(req: StartRequest):
    role = req.role
    experience = req.experience

    previous_evaluation = "No previous answer."
    difficulty = "easy"

    question = generate_question(
        role, experience, previous_evaluation, difficulty, []
    )

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "role": role,
        "experience": experience,
        "difficulty": difficulty,
        "current_question": question,
        "scores": [],
        "question_count": 1,
        "previous_questions": [question]
    }

    return {
        "session_id": session_id,
        "question": question
    }


class AnswerRequest(BaseModel):
    answer: str


@app.post("/interviews/{session_id}/answer")
def submit_answer(session_id: str, req: AnswerRequest):

    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    s = sessions[session_id]

    role = s["role"]
    experience = s["experience"]
    question = s["current_question"]
    answer = req.answer

    evaluation = evaluate_answer(role, question, answer)
    score = evaluation["score"]

    new_difficulty = next_difficulty(s["difficulty"], score)

    s["scores"].append(evaluation)

    # Stop after 3 questions
    if s["question_count"] >= 3:
        summary = final_summary(s["scores"])

        return {
            "message": "Interview completed!",
            "summary": summary,
            "scores": s["scores"]
        }

    # Generate next question
    next_question = generate_question(
        role,
        experience,
        evaluation,
        new_difficulty,
        s["previous_questions"]
    )

    s["current_question"] = next_question
    s["difficulty"] = new_difficulty
    s["question_count"] += 1
    s["previous_questions"].append(next_question)

    return {
        "question": next_question,
        "evaluation": evaluation
    }