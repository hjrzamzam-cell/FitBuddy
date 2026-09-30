from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="FitBuddy AI")
templates = Jinja2Templates(directory="templates")

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key) if api_key else None


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"plan": None, "error": None}
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate_plan(
    request: Request,
    name: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...)
):
    if not client:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "plan": None,
                "error": "Gemini API key is not configured."
            }
        )

    prompt = f"""
Create a safe, beginner-friendly 7-day fitness plan.

User:
Name: {name}
Age: {age}
Weight: {weight} kg
Goal: {goal}
Workout intensity: {intensity}

Give:
1. A 7-day workout schedule
2. Daily workout duration
3. Rest/recovery guidance
4. A short nutrition tip

Keep the advice general and avoid medical claims.
Format the answer clearly with Day 1 through Day 7.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        plan = response.text

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "plan": plan,
                "error": None
            }
        )

    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "plan": None,
                "error": f"Gemini error: {e}"
            }
        )