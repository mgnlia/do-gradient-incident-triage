"use client";

import { useState } from "react";
import { AlertTriangle, Zap, BookOpen, Users, Loader2, ChevronRight } from "lucide-react";
import clsx from "clsx";

interface RunbookStep {
  step_number: number;
  action: string;
  command?: string;
  expected_outcome?: string;
}

interface TriageResult {
  severity: "P1" | "P2" | "P3";
  category: string;
  confidence: number;
  summary: string;
  root_cause_hypothesis: string;
  runbook_steps: RunbookStep[];
  escalation_team: string;
  escalation_reason: string;
  estimated_impact: string;
  model_used: string;
}

const EXAMPLE_ALERTS = [
  {
    label: "Database Connection Pool",
    text: `ALERT: High database connection pool usage
Service: user-service
Environment: production
Timestamp: 2026-02-25T00:30:00Z
Details: PostgreSQL connection pool at 98% capacity (490/500 connections). 
New connection requests timing out after 5000ms. 
Error rate spiking to 23% on /api/user endpoints.
DB host: prod-pg-primary.internal:5432`,
  },
  {
    label: "Memory Leak / OOM",
    text: `CRITICAL: OOMKilled pods in payment-service
Namespace: production
Pod: payment-service-7d4b9c-xk2p9
Reason: OOMKilled (exit code 137)
Memory limit: 512Mi
Last memory reading: 509Mi (99.4%)
Restarts: 12 in last 30 minutes
Impact: Payment processing failing for EU region`,
  },
  {
    label: "5xx Error Spike",
    text: `P1 ALERT: 5xx error rate exceeded threshold
Service: api-gateway
Current error rate: 34.2% (threshold: 5%)
Affected endpoints: /checkout, /cart, /orders
Error breakdown: 502 Bad Gateway (78%), 504 Gateway Timeout (22%)
Upstream: order-service returning errors
Duration: 8 minutes
Revenue impact: ~$12K/min estimated`,
  },
];

export default function Home() {
  const [alertText, setAlertText] = useState("");
  const [serviceName, setServiceName] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<TriageResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleTriage = async () => {
    if (!alertText.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/triage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          alert_text: alertText,
          service_name: serviceName || undefined,
          environment: "production",
        }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Triage failed");
      }

      const data = await res.json();
      setResult(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const severityColors = {
    P1: "bg-red-900/40 border-red-500 text-red-400",
    P2: "bg-orange-900/40 border-orange-500 text-orange-400",
    P3: "bg-yellow-900/40 border-yellow-500 text-yellow-400",
  };

  const severityBadge = {
    P1: "bg-red-500 text-white",
    P2: "bg-orange-500 text-white",
    P3: "bg-yellow-500 text-black",
  };

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#e6edf3]">
      {/* Header */}
      <header className="border-b border-[#30363d] bg-[#161b22]">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
          <div className="w-8 h-8 bg-[#0069ff] rounded flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">AI Incident Triage Assistant</h1>
            <p className="text-xs text-[#8b949e]">Powered by DigitalOcean Gradient™ AI</p>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs text-[#8b949e]">
            <span className="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
            Multi-agent pipeline active
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="space-y-4">
            <div>
              <h2 className="text-xl font-semibold mb-1">Paste Alert or Log</h2>
              <p className="text-sm text-[#8b949e]">
                Paste raw alert text from PagerDuty, Datadog, Grafana, or any monitoring tool.
              </p>
            </div>

            {/* Example alerts */}
            <div>
              <p className="text-xs text-[#8b949e] mb-2">Try an example:</p>
              <div className="flex flex-wrap gap-2">
                {EXAMPLE_ALERTS.map((ex) => (
                  <button
                    key={ex.label}
                    onClick={() => setAlertText(ex.text)}
                    className="text-xs px-3 py-1.5 rounded-full border border-[#30363d] hover:border-[#0069ff] hover:text-[#0069ff] transition-colors"
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-sm text-[#8b949e] block mb-1">Service Name (optional)</label>
              <input
                type="text"
                value={serviceName}
                onChange={(e) => setServiceName(e.target.value)}
                placeholder="e.g. payment-service, api-gateway"
                className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-[#0069ff] placeholder-[#484f58]"
              />
            </div>

            <div>
              <label className="text-sm text-[#8b949e] block mb-1">Alert Text</label>
              <textarea
                value={alertText}
                onChange={(e) => setAlertText(e.target.value)}
                placeholder="Paste your alert, log snippet, or incident description here..."
                rows={12}
                className="w-full bg-[#161b22] border border-[#30363d] rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:border-[#0069ff] placeholder-[#484f58] resize-none"
              />
            </div>

            <button
              onClick={handleTriage}
              disabled={loading || !alertText.trim()}
              className="w-full bg-[#0069ff] hover:bg-[#0052cc] disabled:bg-[#21262d] disabled:text-[#484f58] text-white font-medium py-3 rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing with Gradient AI...
                </>
              ) : (
                <>
                  <AlertTriangle className="w-4 h-4" />
                  Triage Incident
                </>
              )}
            </button>

            {error && (
              <div className="bg-red-900/20 border border-red-800 rounded-lg p-3 text-sm text-red-400">
                {error}
              </div>
            )}
          </div>

          {/* Results Panel */}
          <div className="space-y-4">
            {!result && !loading && (
              <div className="h-full flex items-center justify-center border border-dashed border-[#30363d] rounded-xl p-12 text-center">
                <div>
                  <AlertTriangle className="w-12 h-12 text-[#30363d] mx-auto mb-3" />
                  <p className="text-[#8b949e]">Triage results will appear here</p>
                  <p className="text-xs text-[#484f58] mt-1">Multi-agent AI pipeline: classify → runbook → escalate</p>
                </div>
              </div>
            )}

            {loading && (
              <div className="h-full flex items-center justify-center border border-[#30363d] rounded-xl p-12 text-center">
                <div>
                  <Loader2 className="w-12 h-12 text-[#0069ff] mx-auto mb-3 animate-spin" />
                  <p className="text-[#8b949e]">Running Gradient AI agents...</p>
                  <p className="text-xs text-[#484f58] mt-1">Stage 1: Classify → Stage 2: Runbook</p>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-4">
                {/* Severity Badge */}
                <div className={clsx("border rounded-xl p-4", severityColors[result.severity])}>
                  <div className="flex items-center gap-3 mb-2">
                    <span className={clsx("text-sm font-bold px-2 py-0.5 rounded", severityBadge[result.severity])}>
                      {result.severity}
                    </span>
                    <span className="text-sm font-medium capitalize">{result.category}</span>
                    <span className="ml-auto text-xs opacity-70">
                      {Math.round(result.confidence * 100)}% confidence
                    </span>
                  </div>
                  <p className="font-semibold">{result.summary}</p>
                </div>

                {/* Root Cause */}
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-[#8b949e] mb-2 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> Root Cause Hypothesis
                  </h3>
                  <p className="text-sm">{result.root_cause_hypothesis}</p>
                  <p className="text-xs text-[#8b949e] mt-2">
                    <span className="font-medium">Impact:</span> {result.estimated_impact}
                  </p>
                </div>

                {/* Runbook Steps */}
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-[#8b949e] mb-3 flex items-center gap-2">
                    <BookOpen className="w-4 h-4" /> Runbook Steps
                  </h3>
                  <div className="space-y-3">
                    {result.runbook_steps.map((step) => (
                      <div key={step.step_number} className="flex gap-3">
                        <div className="w-6 h-6 rounded-full bg-[#0069ff]/20 border border-[#0069ff]/40 flex items-center justify-center flex-shrink-0 text-xs text-[#0069ff] font-bold">
                          {step.step_number}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm">{step.action}</p>
                          {step.command && (
                            <code className="text-xs bg-[#0d1117] border border-[#30363d] rounded px-2 py-1 mt-1 block font-mono text-green-400 overflow-x-auto">
                              {step.command}
                            </code>
                          )}
                          {step.expected_outcome && (
                            <p className="text-xs text-[#8b949e] mt-1">
                              <ChevronRight className="w-3 h-3 inline" /> {step.expected_outcome}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Escalation */}
                <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4">
                  <h3 className="text-sm font-semibold text-[#8b949e] mb-2 flex items-center gap-2">
                    <Users className="w-4 h-4" /> Escalation
                  </h3>
                  <p className="font-semibold text-[#0069ff]">{result.escalation_team} Team</p>
                  <p className="text-sm text-[#8b949e] mt-1">{result.escalation_reason}</p>
                </div>

                <p className="text-xs text-[#484f58] text-center">
                  Model: {result.model_used} via DigitalOcean Gradient™ AI
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
