import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from utils.helpers import save_to_json

load_dotenv()

class GeminiChatbot:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("API key not found. Check your .env file.")

        self.client = genai.Client(api_key=api_key)
        self.model = "gemini-3.1-flash-lite-preview"
        self.history = []

    def get_response(self, context, job_role):
        try:
            prompt = f"""
You are an expert ATS (Applicant Tracking System) and resume analyzer.
Your task is to compare a RESUME with a TARGET JOB ROLE and JOB DESCRIPTION.

IMPORTANT RULES:
- Use ONLY the provided context
- Do NOT assume anything outside context
- Be precise and realistic
- Return ONLY valid JSON (no extra text, no markdown, no backticks)

TASKS:
1. Extract key skills from resume
2. Compare with job role: {job_role}
3. Calculate match_score (0-100)
4. Identify missing skills
5. Identify strengths
6. Identify weaknesses
7. Give improvement suggestions

Return format:
{{
  "match_score": 0,
  "strengths": [],
  "missing_skills": [],
  "weaknesses": [],
  "suggestions": []
}}

SCORING LOGIC:
- 80-100 → Strong match
- 60-79 → Moderate match
- 40-59 → Weak match
- Below 40 → Poor match

Context:
{context}
"""

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            text = response.text.strip()

            # ✅ Extract JSON safely
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                text = json_match.group()

            # ✅ Safe JSON parsing
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON from model", "raw": text}

            save_to_json(data)
            return data

        except Exception as e:
            return {"error": str(e)}