"""
AI On-Call Incident Triage Assistant
DigitalOcean Gradient™ AI Hackathon — $20K Prize Pool
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import TriageRequest, TriageResult, HealthResponse, RunbookStep, Severity, Category
from gradient_client import settings

app = FastAPI(
    title="AI Incident Triage Assistant",
    description="Multi-agent incident triage powered by DigitalOcean Gradient™ AI",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DEMO_MODE = not bool(settings.gradient_api_key)


def _demo_triage(alert_text: str, service_name: str = None) -> dict:
    text_lower = alert_text.lower()
    if any(w in text_lower for w in ["down", "outage", "critical", "p1", "fatal", "crash", "500"]):
        severity, confidence = Severity.P1, 0.91
    elif any(w in text_lower for w in ["slow", "latency", "timeout", "error", "fail", "warn"]):
        severity, confidence = Severity.P2, 0.84
    else:
        severity, confidence = Severity.P3, 0.76

    if any(w in text_lower for w in ["db", "database", "postgres", "mysql", "redis", "mongo"]):
        category, team = Category.DATABASE, "Database"
    elif any(w in text_lower for w in ["cpu", "memory", "disk", "node", "pod", "kubernetes", "k8s"]):
        category, team = Category.INFRA, "Platform"
    elif any(w in text_lower for w in ["network", "dns", "timeout", "connection", "firewall"]):
        category, team = Category.NETWORK, "Network"
    elif any(w in text_lower for w in ["auth", "login", "token", "ssl", "cert", "tls"]):
        category, team = Category.SECURITY, "Security"
    else:
        category, team = Category.APP, "Backend"

    svc = service_name or "unknown-service"
    return {
        "severity": severity,
        "category": category,
        "confidence": confidence,
        "summary": f"{severity.value} alert on {svc}: {alert_text[:80]}{'...' if len(alert_text) > 80 else ''}",
        "root_cause_hypothesis": f"Likely {category.value} issue on {svc}. Review recent deployments and resource metrics.",
        "estimated_impact": "Production users affected — investigate immediately." if severity == Severity.P1 else "Partial degradation possible.",
        "escalation_team": team,
        "escalation_reason": f"Alert pattern matches {category.value} domain — {team} team owns this.",
    }


def _demo_runbook(severity: Severity, category: Category) -> list:
    base = [
        RunbookStep(step_number=1, action="Acknowledge the alert in PagerDuty / OpsGenie"),
        RunbookStep(step_number=2, action="Check the service dashboard for error rate and latency spikes"),
        RunbookStep(step_number=3, action="Review recent deployments in the last 30 minutes"),
    ]
    cat_steps = {
        Category.DATABASE: [
            RunbookStep(step_number=4, action="Check DB connection pool utilization", expected_outcome="Pool usage < 80%"),
            RunbookStep(step_number=5, action="Review slow query log for long-running transactions"),
            RunbookStep(step_number=6, action="Verify replication lag on read replicas", command="SHOW SLAVE STATUS\\G"),
        ],
        Category.INFRA: [
            RunbookStep(step_number=4, action="Check node CPU/memory usage", command="kubectl top nodes"),
            RunbookStep(step_number=5, action="Review pod restart counts", command="kubectl get pods --all-namespaces"),
            RunbookStep(step_number=6, action="Check HPA scaling events in the last 10 minutes"),
        ],
        Category.NETWORK: [
            RunbookStep(step_number=4, action="Run traceroute to affected endpoints", command="mtr --report <endpoint>"),
            RunbookStep(step_number=5, action="Check firewall rules and security group changes"),
            RunbookStep(step_number=6, action="Verify DNS resolution for affected domains", command="dig <domain>"),
        ],
        Category.SECURITY: [
            RunbookStep(step_number=4, action="Rotate affected credentials immediately"),
            RunbookStep(step_number=5, action="Review access logs for anomalous patterns"),
            RunbookStep(step_number=6, action="Isolate affected service if breach is confirmed"),
        ],
        Category.APP: [
            RunbookStep(step_number=4, action="Check application logs for stack traces"),
            RunbookStep(step_number=5, action="Review feature flags — roll back recent changes"),
            RunbookStep(step_number=6, action="Check downstream service health (dependencies)"),
        ],
    }
    steps = base + cat_steps.get(category, cat_steps[Category.APP])
    steps.append(RunbookStep(step_number=7, action="Post incident update in #incidents Slack channel"))
    if severity == Severity.P1:
        steps.append(RunbookStep(step_number=8, action="Page engineering manager — P1 requires manager awareness within 15 min"))
    return steps


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(mode="demo" if DEMO_MODE else "live")


@app.post("/triage", response_model=TriageResult)
async def triage_alert(request: TriageRequest):
    if not request.alert_text.strip():
        raise HTTPException(status_code=400, detail="alert_text cannot be empty")

    if DEMO_MODE:
        classification = _demo_triage(request.alert_text, request.service_name)
        runbook_steps = _demo_runbook(classification["severity"], classification["category"])
    else:
        from agents.triage import classify_alert
        from agents.runbook import get_runbook_steps
        classification = await classify_alert(
            alert_text=request.alert_text,
            service_name=request.service_name,
            environment=request.environment,
        )
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
        model_used="gradient-demo" if DEMO_MODE else settings.gradient_model,
    )


@app.post("/webhook/pagerduty")
async def pagerduty_webhook(payload: dict):
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
