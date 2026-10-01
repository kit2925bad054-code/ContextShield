from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from .engines.rule_engine import analyze as analyze_rule
from .engines.ai_engine import analyze_with_ai

app = FastAPI(title="ContextShield API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://contextshield-j58d.vercel.app",
        "https://contextshield-j58d-7w83wa4v8-gridsync1.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "ContextShield"
    }


@app.post("/api/analyze")
async def run(
    input_type: str = Form(...),
    content: str = Form(""),
    mode: str = Form("ai"),
    image: UploadFile | None = File(None)
):

    rule = analyze_rule(content, input_type)

    if mode == "ai":

        ai = await analyze_with_ai(
            content,
            input_type,
            rule,
            image
        )

        if ai.get("result"):
            return ai["result"]

        return {
            **rule,
            "engine": "rule-fallback",
            "ai_status": ai.get("message")
        }

    if mode == "hybrid":

        ai = await analyze_with_ai(
            content,
            input_type,
            rule,
            image
        )

        if ai.get("result"):

            ai_result = ai["result"]

            return {
                **ai_result,
                "engine": "hybrid",
                "rule_score": rule["risk_score"],
                "rule_level": rule["risk_level"],
                "rule_category": rule["category"]
            }

        return {
            **rule,
            "engine": "rule-fallback",
            "ai_status": ai.get("message")
        }

    return rule