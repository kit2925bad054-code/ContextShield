import os
import json
import time

from fastapi import UploadFile


async def analyze_with_ai(
    text,
    input_type="message",
    rule_result=None,
    image: UploadFile | None = None
):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "enabled": False,
            "message": "GEMINI_API_KEY is not configured.",
            "fallback": rule_result
        }

    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        prompt = f"""
You are ContextShield, an explainable scam detection system.

Analyze the provided {input_type} for scam, fraud, phishing,
impersonation, or social-engineering indicators.

For screenshots, analyze BOTH:
1. The actual visual content of the image.
2. The OCR/extracted text provided below.

Pay attention to:
- Sender identity and email/domain
- URLs and domains
- Requests for money or sensitive information
- OTP, PIN, password, bank or card requests
- Urgency and threats
- Fake rewards, jobs, internships, prizes or offers
- Impersonation of companies or organizations
- Suspicious buttons, links, branding or visual elements
- Contradictions between branding and the actual sender/domain
- Context of the complete message

Do NOT mark something as a scam merely because it contains urgency.
Use the complete evidence.

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
- If strong scam indicators are visible, reflect them in the risk score.

OCR TEXT:
{text}
"""

        contents = []

        # Add the actual screenshot to Gemini
        if image is not None:
            image_bytes = await image.read()

            print("🔥 IMAGE RECEIVED:", len(image_bytes), "bytes")
            print("🔥 IMAGE TYPE:", image.content_type)

            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image.content_type or "image/png"
                )
            )

        contents.append(prompt)

        response = None

        # Retry temporary Gemini 503 errors
        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model=model,
                    contents=contents
                )

                break

            except Exception as e:

                error_text = str(e)

                if (
                    "503" not in error_text
                    and "UNAVAILABLE" not in error_text
                ):
                    raise

                print(
                    f"⚠️ Gemini temporarily unavailable. "
                    f"Retry {attempt + 1}/3"
                )

                if attempt < 2:
                    time.sleep(2 ** attempt)

        if response is None:
            return {
                "enabled": False,
                "message": "Gemini temporarily unavailable after retries.",
                "fallback": rule_result
            }

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
            "message": (
                f"AI analysis unavailable: "
                f"{type(e).__name__}: {e}"
            ),
            "fallback": rule_result
        }