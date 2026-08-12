import os
import json

from google import genai
from google.genai import types
from dotenv import load_dotenv

from utils.helpers import save_to_json


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()


class GeminiChatbot:

    def __init__(self):

        # -------------------------------------------------
        # Get API key
        # -------------------------------------------------

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please check your .env file."
            )

        # -------------------------------------------------
        # Initialize Gemini client
        # -------------------------------------------------

        self.client = genai.Client(
            api_key=api_key
        )

        # -------------------------------------------------
        # Configurable Gemini model
        # -------------------------------------------------

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-2.5-flash"
        )

    # -----------------------------------------------------
    # Resume Analysis
    # -----------------------------------------------------

    def get_response(
        self,
        context,
        job_role,
        job_description
    ):

        try:

            # -------------------------------------------------
            # Validate inputs
            # -------------------------------------------------

            if not context or not context.strip():
                return {
                    "error": "No resume context was retrieved."
                }

            if not job_role or not job_role.strip():
                return {
                    "error": "Target job role is required."
                }

            if not job_description or not job_description.strip():
                return {
                    "error": "Job description is required."
                }

            # -------------------------------------------------
            # Prompt
            # -------------------------------------------------

            prompt = f"""
You are an AI-powered resume analysis system.

Your task is to evaluate a candidate's resume against
a target job role and job description.

You are given selected sections of the candidate's
resume retrieved using semantic search.

IMPORTANT RULES:

1. Use ONLY information present in the retrieved resume context.
2. Do NOT invent skills, experience, education,
   certifications or achievements.
3. Do NOT assume a candidate has a skill because it
   is related to another skill.
4. Distinguish explicitly mentioned skills from missing skills.
5. Missing skills should primarily come from requirements
   explicitly mentioned in the job description.
6. Give realistic and actionable recommendations.
7. Keep every list concise and relevant.
8. match_score must be an integer between 0 and 100.

TARGET JOB ROLE:
{job_role}

TARGET JOB DESCRIPTION:
{job_description}

RETRIEVED RESUME CONTEXT:
{context}

Analyze the candidate against the target role.

Identify:

1. Overall match score
2. Candidate strengths
3. Missing skills
4. Resume weaknesses
5. Specific improvement suggestions

Return the result using exactly these fields:

{{
    "match_score": 0,
    "strengths": [],
    "missing_skills": [],
    "weaknesses": [],
    "suggestions": []
}}
"""

            # -------------------------------------------------
            # Gemini API call
            # -------------------------------------------------

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            # -------------------------------------------------
            # Validate response
            # -------------------------------------------------

            if not response or not response.text:
                return {
                    "error": "Gemini returned an empty response."
                }

            # -------------------------------------------------
            # Parse JSON
            # -------------------------------------------------

            try:
                data = json.loads(response.text)

            except json.JSONDecodeError:
                return {
                    "error": "Could not parse Gemini JSON response.",
                    "raw": response.text
                }

            # -------------------------------------------------
            # Validate match score
            # -------------------------------------------------

            score = data.get("match_score", 0)

            try:
                score = int(score)

            except (TypeError, ValueError):
                score = 0

            score = max(
                0,
                min(100, score)
            )

            data["match_score"] = score

            # -------------------------------------------------
            # Validate list fields
            # -------------------------------------------------

            list_fields = [
                "strengths",
                "missing_skills",
                "weaknesses",
                "suggestions"
            ]

            for field in list_fields:

                if not isinstance(
                    data.get(field),
                    list
                ):
                    data[field] = []

            # -------------------------------------------------
            # Save analysis
            # -------------------------------------------------

            save_to_json(data)

            return data

        except Exception as e:

            return {
                "error": str(e)
            }