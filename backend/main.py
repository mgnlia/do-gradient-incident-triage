"""
AI On-Call Incident Triage Assistant
DigitalOcean Gradient™ AI Hackathon — $20K Prize Pool

FastAPI backend that orchestrates a multi-agent triage pipeline using
DigitalOcean Gradient serverless inference.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TriageRequest, TriageResult, HealthResponse
from agents.triage import classify_alert
from agents.runbook import get_runbook_steps
from gradient_client import settings

app = FastAPI(
    title="AI Incident Triage Assistant",
    description="Multi-agent incident triage powered by DigitalOcean Gradient™ AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/triage", response_model=TriageResult)
async def triage_alert(request: TriageRequest):
    """
    Main triage endpoint. Runs a 2-stage Gradient AI pipeline:
    1. Classify severity, category, root cause
    2. Generate runbook steps
    """
    if not request.alert_text.strip():
        raise HTTPException(status_code=400, detail="alert_text cannot be empty")

    if not settings.gradient_api_key:
        raise HTTPException(
            status_code=503,
            detail="GRADIENT_API_KEY not configured. Set it in backend/.env"
        )

    # Stage 1: Classify the alert
    classification = await classify_alert(
        alert_text=request.alert_text,
        service_name=request.service_name,
        environment=request.environment,
    )

    # Stage 2: Get runbook steps
    runbook_steps = await get_runbook_steps(
        severity=classification["severity"].value,
        category=classification["category"].value,
        summary=classification["summary"],
        root_cause=classification["root_cause_hypothesis"],
        service_name=request.service_name,
    )

    return TriageResult(
        severity=classification["severity"],
        category=classification["category"],
        confidence=classification["confidence"],
        summary=classification["summary"],
        root_cause_hypothesis=classification["root_cause_hypothesis"],
        runbook_steps=runbook_steps,
        escalation_team=classification["escalation_team"],
        escalation_reason=classification["escalation_reason"],
        estimated_impact=classification["estimated_impact"],
        raw_alert=request.alert_text,
        model_used=settings.gradient_model,
    )


@app.post("/webhook/pagerduty")
async def pagerduty_webhook(payload: dict):
    """Accept PagerDuty webhook and auto-triage."""
    # Extract alert text from PagerDuty payload
    alert_text = ""
    service_name = ""

    if "messages" in payload:
        for msg in payload["messages"]:
            incident = msg.get("incident", {})
            alert_text = incident.get("description", "") or incident.get("title", "")
            service_name = incident.get("service", {}).get("name", "")
            break

    if not alert_text:
        raise HTTPException(status_code=400, detail="Could not extract alert from PagerDuty payload")

    req = TriageRequest(alert_text=alert_text, service_name=service_name, source="pagerduty")
    return await triage_alert(req)
