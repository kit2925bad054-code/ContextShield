# ContextShield — Rule + AI Architecture

This package separates the deterministic Rule Engine from the optional AI Engine.

## 1. Backend

```powershell
cd backend
py -m pip install -r requirements.txt
py -m uvicorn app.main:app --reload
```

Open:

`http://127.0.0.1:8000/docs`

Health:

`http://127.0.0.1:8000/api/health`

## 2. Rule engine

Default mode is `rule`.

```json
{
  "input_type": "message",
  "content": "hi",
  "mode": "rule"
}
```

The rule engine is deterministic and does not require an API key.

## 3. AI engine

Install the optional dependency:

```powershell
py -m pip install -r requirements-ai.txt
```

Create `.env` from `.env.example` and put your Gemini key there.

AI mode:

```json
{
  "input_type": "message",
  "content": "Your account will be blocked. Pay now...",
  "mode": "ai"
}
```

Hybrid mode runs the rule engine first and uses AI when configured.

## 4. Important

OCR, QR decoding, live website inspection, external threat-intelligence feeds and production database integrations are provided as adapters/interfaces so the project can be extended without breaking the working rule-based demo.

The project does not claim that placeholder adapters are already live integrations.
