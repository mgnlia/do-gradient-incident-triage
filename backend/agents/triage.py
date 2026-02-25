"""
Triage Classifier Agent — uses DigitalOcean Gradient serverless inference
to classify alert severity, category, and generate a root-cause hypothesis.
"""
import json
from gradient_client import get_gradient_client, settings
from models import Severity, Category

TRIAGE_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) with 10+ years of experience.
Your job is to analyze raw incident alerts and classify them accurately.

You MUST respond with valid JSON only — no markdown, no explanation outside the JSON.

Response schema:
{
  "severity": "P1" | "P2" | "P3",
  "category": "infra" | "app" | "database" | "network" | "security" | "unknown",
  "confidence": 0.0-1.0,
  "summary": "one-sentence summary of the issue",
  "root_cause_hypothesis": "most likely root cause based on the alert",
  "estimated_impact": "who/what is affected and how severely",
  "escalation_team": "team name (e.g. Platform, Backend, Database, Security, Network)",
  "escalation_reason": "why this team should handle it"
}

Severity guide:
- P1: Production is completely down, revenue impact, data loss risk
- P2: Significant degradation, partial outage, performance severely impacted
- P3: Minor issue, single service degraded, no immediate user impact
"""


async def classify_alert(alert_text: str, service_name: str = None, environment: str = "production") -> dict:
    """
    Classify an alert using DigitalOcean Gradient serverless inference.
    Returns parsed triage classification dict.
    """
    client = get_gradient_client()

    context = f"Service: {service_name or 'unknown'}\nEnvironment: {environment}\n\nAlert:\n{alert_text}"

    response = await client.chat.completions.create(
        model=settings.gradient_model,
        messages=[
            {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.1,  # Low temp for consistent classification
        max_tokens=512,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    # Normalize and validate
    result["severity"] = Severity(result.get("severity", "P3"))
    result["category"] = Category(result.get("category", "unknown"))
    result["confidence"] = float(result.get("confidence", 0.5))

    return result
