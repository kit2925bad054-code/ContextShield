from dotenv import load_dotenv
load_dotenv()


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .engines.rule_engine import analyze as analyze_rule
from .engines.ai_engine import analyze_with_ai

app = FastAPI(title="ContextShield API", version="2.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://contextshield-j58d.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    input_type: str
    content: str = ""
    mode: str = "ai"

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ContextShield"}

@app.post("/api/analyze")
def run(req: AnalyzeRequest):

    rule = analyze_rule(req.content, req.input_type)

    if req.mode == "ai":
        ai = analyze_with_ai(
            req.content,
            req.input_type,
            rule
        )

        if ai.get("result"):
            return ai["result"]

        return {
            **rule,
            "engine": "rule-fallback",
            "ai_status": ai.get("message")
        }

    if req.mode == "hybrid":

        ai = analyze_with_ai(
            req.content,
            req.input_type,
            rule
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