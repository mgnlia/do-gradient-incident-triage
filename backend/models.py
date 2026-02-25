from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class Severity(str, Enum):
    P1 = "P1"  # Critical — production down
    P2 = "P2"  # High — major degradation
    P3 = "P3"  # Medium — minor issue


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
    source: Optional[str] = "manual"  # manual | pagerduty | datadog | grafana


class RunbookStep(BaseModel):
    step_number: int
    action: str
    command: Optional[str] = None
    expected_outcome: Optional[str] = None


class TriageResult(BaseModel):
    severity: Severity
    category: Category
    confidence: float  # 0.0 - 1.0
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
    version: str = "0.1.0"
