"""
CareerCompass AI — LLM integration layer.

Calls the Google Gemini API via the official Google Gen AI SDK to power
career guidance, roadmap generation, resume review, and skill-gap analysis.

main.py should never call the Gemini SDK directly — it always goes through here.
"""

import json
import os
from typing import Any, Dict

from fastapi import HTTPException
from google import genai
from google.genai import errors as genai_errors
from google.genai import types

# gemini-3.6-flash is the current stable, general-availability flash model as of
# mid-2026 and is available to newly created API keys. Older model strings like
# gemini-2.5-flash and gemini-2.0-flash have been cut off for new keys even
# though their official shutdown dates haven't passed yet — Google appears to
# restrict some older stable models to accounts with prior usage. If Google
# ships a newer stable flash model later, override via GEMINI_MODEL rather than
# editing code.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    """Lazily create the Gemini client so the module can be imported (e.g. in
    tests) even when GEMINI_API_KEY isn't set yet."""
    global _client
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured. Add a real key to your .env file.",
        )
    if _client is None:
        _client = genai.Client(api_key=api_key)
    return _client


def _profile_summary(profile: Dict[str, Any]) -> str:
    parts = []
    if profile.get("branch"):
        parts.append(f"Branch: {profile['branch']}")
    if profile.get("semester"):
        parts.append(f"Semester: {profile['semester']}")
    if profile.get("skills"):
        skills = profile["skills"]
        skills_str = ", ".join(skills) if isinstance(skills, list) else skills
        parts.append(f"Current skills: {skills_str}")
    if profile.get("interests"):
        interests = profile["interests"]
        interests_str = ", ".join(interests) if isinstance(interests, list) else interests
        parts.append(f"Interests: {interests_str}")
    if profile.get("goal"):
        parts.append(f"Career goal: {profile['goal']}")
    return "\n".join(parts) if parts else "No profile information provided yet."


def _generate(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    client = _get_client()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json" if json_mode else "text/plain",
                temperature=0.4,
            ),
        )
    except genai_errors.APIError as exc:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {exc}") from exc

    return response.text or ""


def _parse_json(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise HTTPException(status_code=502, detail="Received a malformed response from the AI model.") from exc


def get_career_guidance(profile: Dict[str, Any], question: str) -> str:
    """Answer a free-form career question, grounded in the student's profile."""
    system_prompt = (
        "You are CareerCompass AI, a supportive and knowledgeable career mentor for "
        "engineering students. Give concrete, specific, encouraging guidance. "
        "Use short paragraphs or bullet points. Avoid generic filler."
    )
    user_prompt = (
        f"Student profile:\n{_profile_summary(profile)}\n\n"
        f"Student's question:\n{question}"
    )
    return _generate(system_prompt, user_prompt).strip()


def generate_roadmap(profile: Dict[str, Any], domain: str) -> Dict[str, Any]:
    """Generate a structured, phased learning roadmap for a target domain."""
    system_prompt = (
        "You are CareerCompass AI, a career mentor for engineering students. "
        "Produce a learning roadmap as strict JSON with this exact shape:\n"
        '{"domain": string, "stages": [{"title": string, "duration": string, '
        '"topics": [string], "resources": [string]}]}\n'
        "Include 3 to 5 stages, ordered from foundational to advanced. "
        "Respond with JSON only, no prose outside the JSON object."
    )
    user_prompt = (
        f"Student profile:\n{_profile_summary(profile)}\n\n"
        f"Target domain: {domain}\n"
        "Tailor the roadmap to the student's current skill level where possible."
    )
    raw = _generate(system_prompt, user_prompt, json_mode=True)
    return _parse_json(raw)


def review_resume(resume_text: str) -> Dict[str, Any]:
    """Analyze resume text and return structured strengths/improvements."""
    system_prompt = (
        "You are CareerCompass AI, reviewing an engineering student's resume. "
        "Respond with strict JSON in this exact shape:\n"
        '{"strengths": [string], "improvements": [string], "summary": string}\n'
        "List 3-6 strengths and 3-6 concrete, actionable improvements. "
        "Keep the summary to 2-3 sentences. Respond with JSON only."
    )
    user_prompt = f"Resume text:\n{resume_text}"
    raw = _generate(system_prompt, user_prompt, json_mode=True)
    return _parse_json(raw)


def analyze_skill_gap(profile: Dict[str, Any], target_role: str) -> Dict[str, Any]:
    """Compare the student's current skills against a target role."""
    system_prompt = (
        "You are CareerCompass AI, analyzing a skill gap for an engineering student. "
        "Respond with strict JSON in this exact shape:\n"
        '{"target_role": string, "known_skills": [string], "missing_skills": [string], '
        '"recommended_resources": [string]}\n'
        "known_skills should reflect skills the student already has that are relevant "
        "to the target role. missing_skills should be specific, not generic. "
        "recommended_resources should be concrete (courses, certifications, project ideas). "
        "Respond with JSON only."
    )
    user_prompt = (
        f"Student profile:\n{_profile_summary(profile)}\n\n"
        f"Target role: {target_role}"
    )
    raw = _generate(system_prompt, user_prompt, json_mode=True)
    return _parse_json(raw)
