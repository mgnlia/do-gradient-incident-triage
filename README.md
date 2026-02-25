# 🚨 AI On-Call Incident Triage Assistant

> **DigitalOcean Gradient™ AI Hackathon Submission** — $20K Prize Pool

An AI-powered incident triage system built on **DigitalOcean Gradient™ AI Platform** that classifies alert severity, suggests runbook steps, and routes incidents to the right responder — all in seconds.

## 🎯 What It Does

1. **Ingest** — Paste raw logs/alerts or connect via webhook (PagerDuty, Datadog, Grafana)
2. **Classify** — Gradient multi-agent pipeline classifies severity (P1/P2/P3) with reasoning
3. **Runbook** — RAG-powered knowledge base suggests step-by-step remediation
4. **Route** — Recommends on-call team based on service ownership map

## 🏗️ Architecture

```
Alert Input (paste/webhook)
        ↓
[Gradient Agent: Triage Classifier]
  - Severity: P1/P2/P3
  - Category: infra/app/db/network
  - Confidence score
        ↓
[Gradient Agent: Runbook Retriever]  ← Knowledge Base (RAG)
  - Matches alert to runbook
  - Suggests top 5 remediation steps
        ↓
[Gradient Agent: Escalation Router]
  - Determines on-call owner
  - Generates incident summary
        ↓
Next.js Dashboard (Vercel)
```

## 🛠️ Stack

- **AI Platform:** DigitalOcean Gradient™ AI (multi-agent + RAG knowledge base)
- **Backend:** FastAPI (Python)
- **Frontend:** Next.js 14 + Tailwind CSS
- **Deploy:** Vercel (frontend) + DigitalOcean App Platform (backend)

## 🚀 Quick Start

### Prerequisites
- DigitalOcean account with Gradient AI access
- `GRADIENT_API_KEY` from DO console
- Node.js 18+, Python 3.11+

### Backend
```bash
cd backend
uv sync
uv run uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```env
# backend/.env
GRADIENT_API_KEY=your_do_gradient_key
GRADIENT_AGENT_ID=your_agent_id
GRADIENT_KNOWLEDGE_BASE_ID=your_kb_id

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📁 Project Structure

```
do-gradient-triage/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── agents/
│   │   ├── triage.py        # Severity classifier agent
│   │   ├── runbook.py       # RAG runbook retriever
│   │   └── router.py        # Escalation router
│   ├── models.py            # Pydantic schemas
│   ├── gradient_client.py   # DO Gradient SDK wrapper
│   └── pyproject.toml
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main dashboard
│   │   ├── components/
│   │   │   ├── AlertInput.tsx
│   │   │   ├── TriageResult.tsx
│   │   │   └── RunbookSteps.tsx
│   │   └── api/
│   │       └── triage/route.ts
│   ├── package.json
│   └── tailwind.config.ts
├── runbooks/                # Sample runbook knowledge base
│   ├── high-cpu.md
│   ├── memory-leak.md
│   ├── db-connection-pool.md
│   └── 5xx-spike.md
└── README.md
```

## 🏆 Hackathon Criteria

- **Innovation:** Multi-agent pipeline with RAG specifically for SRE/DevOps workflows
- **DO Platform Usage:** Gradient AI agents + knowledge bases + serverless inference
- **Real-world Impact:** Reduces MTTR by automating first-response triage
- **Production-ready:** Deployed on DO App Platform with proper error handling
