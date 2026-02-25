from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Severity(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class Category(str, Enum):
    INFRA = "infra"
    APP = "app"
    DATABASE = "database"
    NETWORK = "network"
    SECURITY = "security"
    UNKNOWN = "unknown"


class TriageRequest(BaseModel):
    alert_text: str
    service_name: Optional[str] = None
    environment: Optional[str] = "production"
    source: Optional[str] = "manual"


class RunbookStep(BaseModel):
    step_number: int
    action: str
    command: Optional[str] = None
    expected_outcome: Optional[str] = None


class TriageResult(BaseModel):
    severity: Severity
    category: Category
    confidence: float
    summary: str
    root_cause_hypothesis: str
    runbook_steps: List[RunbookStep]
    escalation_team: str
    escalation_reason: str
    estimated_impact: str
    raw_alert: str
    model_used: str = "gradient-inference"


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "AI Incident Triage Assistant"
    version: str = "0.1.0"
    mode: str = "live"
