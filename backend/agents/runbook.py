"""
Runbook Retriever Agent — uses DigitalOcean Gradient RAG knowledge base
to retrieve relevant runbook steps for a classified incident.
"""
import json
from gradient_client import get_gradient_client, settings
from models import RunbookStep

RUNBOOK_SYSTEM_PROMPT = """You are an expert SRE runbook generator. Given an incident classification,
generate concrete, actionable remediation steps.

You MUST respond with valid JSON only.

Response schema:
{
  "runbook_steps": [
    {
      "step_number": 1,
      "action": "description of what to do",
      "command": "optional shell/kubectl/etc command",
      "expected_outcome": "what you should see if this works"
    }
  ]
}

Rules:
- Provide 3-7 steps depending on severity
- Steps must be ordered from immediate triage to full resolution
- Include real commands where applicable (kubectl, psql, curl, etc.)
- P1 steps should focus on mitigation first, then diagnosis
- P2/P3 steps can be more diagnostic
"""


async def get_runbook_steps(
    severity: str,
    category: str,
    summary: str,
    root_cause: str,
    service_name: str = None,
) -> list[RunbookStep]:
    """
    Generate runbook steps for an incident using Gradient inference.
    In production, this would query a Gradient knowledge base (RAG).
    """
    client = get_gradient_client()

    context = f"""Incident Details:
- Severity: {severity}
- Category: {category}
- Summary: {summary}
- Root Cause Hypothesis: {root_cause}
- Service: {service_name or 'unknown'}

Generate step-by-step remediation runbook."""

    response = await client.chat.completions.create(
        model=settings.gradient_model,
        messages=[
            {"role": "system", "content": RUNBOOK_SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.2,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)

    steps = []
    for step_data in result.get("runbook_steps", []):
        steps.append(RunbookStep(
            step_number=step_data.get("step_number", len(steps) + 1),
            action=step_data.get("action", ""),
            command=step_data.get("command"),
            expected_outcome=step_data.get("expected_outcome"),
        ))

    return steps
