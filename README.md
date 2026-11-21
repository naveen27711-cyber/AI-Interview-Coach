
# AI Interview Coach

An AI-powered interview practice application that helps users prepare for technical interviews through interactive questions and AI-based answer evaluation.

## Features

- Select a target job role and experience level.
- Generate interview questions using Gemini AI.
- Evaluate answers and provide scores and feedback.
- Adjust question difficulty based on performance.
- Display a final performance summary.
- Handle API errors and invalid inputs.

## Technologies Used

- Python
- FastAPI (Backend)
- Streamlit (Frontend)
- Google Gemini API
- Pydantic
- Requests

## Project Architecture

Streamlit Frontend → FastAPI Backend → Gemini API

The frontend sends user inputs to the backend. FastAPI communicates with Gemini to generate interview questions and evaluate answers.

## How to Run Locally

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Add your Gemini API key to a `.env` file:

```env
GEMINI_API_KEY=your_api_key
```

5. Start the FastAPI backend:

```bash
python -m uvicorn backend.main:app --reload
```

6. In another terminal, start Streamlit:

```bash
python -m streamlit run frontend/app.py
```

## Security

The Gemini API key is stored in environment variables and should never be committed to GitHub.