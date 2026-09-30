import os
import json


def analyze_with_ai(text, input_type="message", rule_result=None):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "message": "GEMINI_API_KEY is not configured.",
            "fallback": rule_result
        }

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        prompt = f"""
You are ContextShield, an explainable scam detection system.

Analyze the following {input_type} for scam or fraud indicators.

Return ONLY valid JSON:

{{
    "risk_score": 0,
    "risk_level": "LOW",
    "category": "General",
    "language": "English",
    "reasons": [],
    "safe_action": ""
}}

Rules:
- risk_score must be between 0 and 100.
- risk_level must be LOW, MEDIUM, or HIGH.
- Explain only observable evidence.
- Do not invent facts.
- Give practical safety advice.

INPUT:
{text}
"""

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )

        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "")
            raw = raw.replace("```", "")
            raw = raw.strip()

        data = json.loads(raw)

        data["engine"] = "ai"
        data["input_type"] = input_type
        data["official_url"] = None

        return {
            "enabled": True,
            "result": data
        }

    except Exception as e:
        print("🔥 AI ERROR:", repr(e))

        return {
            "enabled": False,
            "message": f"AI analysis unavailable: {type(e).__name__}: {e}",
            "fallback": rule_result
        }