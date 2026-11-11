"use client";

import { useState, useRef } from "react";

type AgentMessage = {
  role: string;
  content: string;
  thought: string;
  confidence: number;
  timestamp: string;
  metadata?: Record<string, any>;
};

type FinalReport = {
  overall_assessment: string;
  claim_count: number;
  issues_found: number;
  high_severity: number;
  medium_severity: number;
  knowledge_items_used: number;
  recommendations: string[];
  detailed_issues: Array<{
    type: string;
    severity: string;
    claim: string;
    matched_myth?: string | null;
    explanation: string;
    suggestion: string;
  }>;
  agent_collaboration_note: string;
};

type ReviewResult = {
  document_id: string;
  extracted_claims: string[];
  retrieved_knowledge: any[];
  potential_issues: any[];
  agent_trace: AgentMessage[];
  final_report: FinalReport | null;
};

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const AGENT_COLORS: Record<string, string> = {
  viewer: "from-cyan-500 to-blue-600",
  thinker: "from-violet-500 to-purple-600",
  recall: "from-emerald-500 to-teal-600",
  checker: "from-amber-500 to-orange-600",
  synthesizer: "from-rose-500 to-pink-600",
};

const AGENT_ICONS: Record<string, string> = {
  viewer: "👁️",
  thinker: "🧠",
  recall: "📚",
  checker: "🔍",
  synthesizer: "✨",
};

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ReviewResult | null>(null);
  const [activeTab, setActiveTab] = useState<"trace" | "report" | "claims">("trace");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setError(null);
    }
  };

  const runReview = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      let data: any;

      if (file) {
        const form = new FormData();
        form.append("file", file);
        const res = await fetch(`${API_BASE}/api/review`, {
          method: "POST",
          body: form,
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Server error ${res.status}`);
        }
        data = await res.json();
        setResult(data.result);
      } else if (textInput.trim().length > 30) {
        const res = await fetch(`${API_BASE}/api/review-text`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: textInput }),
        });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || `Server error ${res.status}`);
        }
        data = await res.json();
        setResult(data.result);
      } else {
        throw new Error("Please upload a file or paste at least ~30 characters of text.");
      }
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setFile(null);
    setTextInput("");
    setResult(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
      <header className="border-b border-slate-800/80 bg-slate-950/60 backdrop-blur-md sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-cyan-500/20">
              ⚡
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                Neuromorphic Multi-Agent Reviewer
              </h1>
              <p className="text-xs text-slate-400">
                See → Think → Recall → Check → Synthesize · Anti-hallucination pipeline
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-slate-500">
            <span className="px-2 py-1 rounded-full bg-slate-800/80 border border-slate-700">
              5 Agents
            </span>
            <span className="px-2 py-1 rounded-full bg-slate-800/80 border border-slate-700">
              Grounded KB
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        <section className="grid md:grid-cols-2 gap-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 shadow-xl">
            <h2 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
              <span className="text-lg">📄</span> Upload Research Document
            </h2>
            <div
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors cursor-pointer
                ${file ? "border-cyan-500/60 bg-cyan-500/5" : "border-slate-700 hover:border-slate-500"}`}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.pdf,.docx,.doc"
                className="hidden"
                onChange={handleFileChange}
              />
              {file ? (
                <div>
                  <p className="text-cyan-300 font-medium">{file.name}</p>
                  <p className="text-xs text-slate-500 mt-1">
                    {(file.size / 1024).toFixed(1)} KB · Click to change
                  </p>
                </div>
              ) : (
                <div>
                  <p className="text-slate-400">Drop or click to upload</p>
                  <p className="text-xs text-slate-600 mt-1">.txt · .pdf · .docx</p>
                </div>
              )}
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 shadow-xl">
            <h2 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
              <span className="text-lg">✍️</span> Or Paste Text
            </h2>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="Paste a research abstract, paragraph, or claims about neuromorphic computing, SNNs, Loihi, STDP..."
              className="w-full h-32 bg-slate-950/80 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 resize-none"
            />
          </div>
        </section>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={runReview}
            disabled={loading || (!file && textInput.trim().length < 30)}
            className="px-6 py-2.5 rounded-xl font-medium bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-cyan-500/20 transition-all"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Agents working…
              </span>
            ) : (
              "Run Multi-Agent Review"
            )}
          </button>
          <button
            onClick={clearAll}
            className="px-4 py-2.5 rounded-xl text-sm text-slate-400 hover:text-slate-200 border border-slate-700 hover:border-slate-500 transition"
          >
            Clear
          </button>
          {error && (
            <p className="text-rose-400 text-sm ml-2">{error}</p>
          )}
        </div>

        {result && (
          <section className="space-y-6">
            {result.final_report && (
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
                <SummaryCard label="Claims Extracted" value={result.final_report.claim_count} color="cyan" />
                <SummaryCard label="Issues Found" value={result.final_report.issues_found} color={result.final_report.issues_found > 0 ? "amber" : "emerald"} />
                <SummaryCard label="High Severity" value={result.final_report.high_severity} color={result.final_report.high_severity > 0 ? "rose" : "emerald"} />
                <SummaryCard label="Knowledge Used" value={result.final_report.knowledge_items_used} color="violet" />
              </div>
            )}

            {result.final_report && (
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
                <h3 className="text-sm font-medium text-slate-400 mb-2">Overall Assessment</h3>
                <p className="text-slate-200 leading-relaxed">
                  {result.final_report.overall_assessment}
                </p>
              </div>
            )}

            <div className="flex gap-1 border-b border-slate-800">
              {(
                [
                  ["trace", "Agent Trace (See · Think · Recall)"],
                  ["report", "Detailed Issues & Recommendations"],
                  ["claims", "Extracted Claims"],
                ] as const
              ).map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => setActiveTab(id)}
                  className={`px-4 py-2.5 text-sm font-medium transition border-b-2 -mb-px
                    ${
                      activeTab === id
                        ? "border-cyan-500 text-cyan-300"
                        : "border-transparent text-slate-500 hover:text-slate-300"
                    }`}
                >
                  {label}
                </button>
              ))}
            </div>

            {activeTab === "trace" && (
              <div className="space-y-4">
                {result.agent_trace.map((msg, idx) => (
                  <div key={idx} className="rounded-2xl border border-slate-800 bg-slate-900/40 overflow-hidden">
                    <div className={`px-4 py-3 bg-gradient-to-r ${AGENT_COLORS[msg.role] || "from-slate-700 to-slate-800"} flex items-center justify-between`}>
                      <div className="flex items-center gap-2 font-medium">
                        <span>{AGENT_ICONS[msg.role] || "🤖"}</span>
                        <span className="capitalize">{msg.role} Agent</span>
                      </div>
                      <span className="text-xs bg-black/20 px-2 py-0.5 rounded-full">
                        Confidence {(msg.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <div className="p-4 space-y-3">
                      <p className="text-slate-200">{msg.content}</p>
                      {msg.thought && (
                        <div className="rounded-xl bg-slate-950/60 border border-slate-800 p-3">
                          <p className="text-xs text-slate-500 mb-1 font-medium uppercase tracking-wider">
                            Internal Reasoning (anti-hallucination)
                          </p>
                          <p className="text-sm text-slate-400 font-mono leading-relaxed">
                            {msg.thought}
                          </p>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "report" && result.final_report && (
              <div className="space-y-6">
                {result.final_report.detailed_issues.length > 0 ? (
                  <div className="space-y-3">
                    <h3 className="text-sm font-medium text-slate-300">
                      Potential Mistakes / Hallucination Risks
                    </h3>
                    {result.final_report.detailed_issues.map((issue, i) => (
                      <div
                        key={i}
                        className={`rounded-xl border p-4 ${
                          issue.severity === "high"
                            ? "border-rose-500/40 bg-rose-500/5"
                            : "border-amber-500/30 bg-amber-500/5"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`text-xs font-semibold uppercase px-2 py-0.5 rounded ${
                            issue.severity === "high" ? "bg-rose-500/20 text-rose-300" : "bg-amber-500/20 text-amber-300"
                          }`}>
                            {issue.severity}
                          </span>
                          <span className="text-xs text-slate-500">{issue.type}</span>
                        </div>
                        <p className="text-sm text-slate-300 mb-2 italic">“{issue.claim}”</p>
                        <p className="text-sm text-slate-400 mb-1">{issue.explanation}</p>
                        <p className="text-xs text-cyan-400/90">💡 {issue.suggestion}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-emerald-400/90 text-sm">
                    No strong red flags detected against the knowledge base.
                  </p>
                )}

                <div>
                  <h3 className="text-sm font-medium text-slate-300 mb-2">Recommendations</h3>
                  <ul className="space-y-1.5">
                    {result.final_report.recommendations.map((rec, i) => (
                      <li key={i} className="flex gap-2 text-sm text-slate-400">
                        <span className="text-cyan-500">→</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>

                <p className="text-xs text-slate-600 border-t border-slate-800 pt-4">
                  {result.final_report.agent_collaboration_note}
                </p>
              </div>
            )}

            {activeTab === "claims" && (
              <div className="space-y-2">
                {result.extracted_claims.length === 0 ? (
                  <p className="text-slate-500 text-sm">No claims extracted.</p>
                ) : (
                  result.extracted_claims.map((c, i) => (
                    <div key={i} className="rounded-xl border border-slate-800 bg-slate-900/40 px-4 py-3 text-sm text-slate-300">
                      <span className="text-slate-600 mr-2">#{i + 1}</span>
                      {c}
                    </div>
                  ))
                )}
              </div>
            )}
          </section>
        )}

        {!result && !loading && (
          <section className="rounded-2xl border border-slate-800/80 bg-slate-900/30 p-6 mt-8">
            <h2 className="text-sm font-medium text-slate-300 mb-4">
              How the multi-agent anti-hallucination pipeline works
            </h2>
            <div className="grid sm:grid-cols-5 gap-3 text-center">
              {[
                { icon: "👁️", name: "Viewer", desc: "Sees the document & extracts claims" },
                { icon: "🧠", name: "Thinker", desc: "Reasons about risk areas & structure" },
                { icon: "📚", name: "Recall", desc: "Retrieves grounded neuromorphic knowledge" },
                { icon: "🔍", name: "Checker", desc: "Detects myths, overclaims & errors" },
                { icon: "✨", name: "Synthesizer", desc: "Produces the final actionable report" },
              ].map((a) => (
                <div key={a.name} className="rounded-xl bg-slate-950/50 border border-slate-800 p-3">
                  <div className="text-2xl mb-1">{a.icon}</div>
                  <div className="text-sm font-medium text-slate-200">{a.name}</div>
                  <div className="text-xs text-slate-500 mt-1">{a.desc}</div>
                </div>
              ))}
            </div>
            <p className="text-xs text-slate-600 mt-4 text-center">
              Each agent externalizes its reasoning (see / think / recall) so hallucinations cannot stay silent.
            </p>
          </section>
        )}
      </main>

      <footer className="border-t border-slate-900 mt-12 py-6 text-center text-xs text-slate-600">
        Neuromorphic AI Researcher · Multi-Agent Document Reviewer · Local-first
      </footer>
    </div>
  );
}

function SummaryCard({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const colors: Record<string, string> = {
    cyan: "from-cyan-500/20 to-cyan-600/5 border-cyan-500/30 text-cyan-300",
    amber: "from-amber-500/20 to-amber-600/5 border-amber-500/30 text-amber-300",
    rose: "from-rose-500/20 to-rose-600/5 border-rose-500/30 text-rose-300",
    emerald: "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30 text-emerald-300",
    violet: "from-violet-500/20 to-violet-600/5 border-violet-500/30 text-violet-300",
  };
  return (
    <div className={`rounded-xl border bg-gradient-to-br p-4 ${colors[color] || colors.cyan}`}>
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  );
}
