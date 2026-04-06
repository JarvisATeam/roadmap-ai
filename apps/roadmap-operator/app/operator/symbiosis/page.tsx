"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type {
  SymbioticDecisionPillars,
  SymbioticChallengeToken,
  ContradictionPair,
  ConsequenceMemoryEvent,
} from "@roadmap/operator-contracts";

// API Client functions
async function fetchDecisionPillars(): Promise<SymbioticDecisionPillars | null> {
  try {
    const res = await fetch("/api/symbiosis/decision");
    const data = await res.json();
    return data.sample || null;
  } catch {
    return null;
  }
}

async function fetchChallenges(): Promise<SymbioticChallengeToken[]> {
  try {
    const res = await fetch("/api/symbiosis/challenge");
    const data = await res.json();
    return data.challenges || [];
  } catch {
    return [];
  }
}

async function fetchContradictions(): Promise<ContradictionPair[]> {
  try {
    const res = await fetch("/api/symbiosis/contradictions");
    const data = await res.json();
    return data.contradictions || [];
  } catch {
    return [];
  }
}

async function fetchMemories(): Promise<ConsequenceMemoryEvent[]> {
  try {
    const res = await fetch("/api/symbiosis/memory?limit=5");
    const data = await res.json();
    return data.memories || [];
  } catch {
    return [];
  }
}

async function submitChallenge(
  originalOutput: string,
  humanChallenge: string,
  challengeType: string
): Promise<boolean> {
  try {
    const res = await fetch("/api/symbiosis/challenge", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ originalOutput, humanChallenge, challengeType }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

// Helper functions
function getRiskColor(level: string): string {
  switch (level) {
    case "critical":
      return "bg-red-100 text-red-800";
    case "high":
      return "bg-orange-100 text-orange-800";
    case "medium":
      return "bg-yellow-100 text-yellow-800";
    case "low":
    default:
      return "bg-green-100 text-green-800";
  }
}

function getCoCreationColor(score: number): string {
  if (score >= 8) return "bg-purple-100 text-purple-800";
  if (score >= 5) return "bg-blue-100 text-blue-800";
  return "bg-gray-100 text-gray-800";
}

export default function SymbiosisPage() {
  const [pillars, setPillars] = useState<SymbioticDecisionPillars | null>(null);
  const [challenges, setChallenges] = useState<SymbioticChallengeToken[]>([]);
  const [contradictions, setContradictions] = useState<ContradictionPair[]>([]);
  const [memories, setMemories] = useState<ConsequenceMemoryEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"pillars" | "challenges" | "contradictions" | "memory">("pillars");

  // Challenge form state
  const [challengeForm, setChallengeForm] = useState({
    original: "",
    challenge: "",
    type: "correct",
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    const [p, c, ct, m] = await Promise.all([
      fetchDecisionPillars(),
      fetchChallenges(),
      fetchContradictions(),
      fetchMemories(),
    ]);
    setPillars(p);
    setChallenges(c);
    setContradictions(ct);
    setMemories(m);
    setLoading(false);
  }

  async function handleSubmitChallenge() {
    const success = await submitChallenge(
      challengeForm.original,
      challengeForm.challenge,
      challengeForm.type
    );
    if (success) {
      setChallengeForm({ original: "", challenge: "", type: "correct" });
      await loadData();
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Symbiosis Layer</h1>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Symbiosis Layer</h1>
            <p className="text-sm text-gray-600 mt-1">
              Menneske-AI samskapelse og beslutningsstøtte
            </p>
          </div>
          <Button onClick={loadData} variant="secondary" size="sm">
            Refresh
          </Button>
        </div>

        {/* Metrics Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card title="Co-Creation Score" className="bg-gradient-to-br from-purple-50 to-blue-50">
            <div className="text-3xl font-bold text-purple-900">
              {pillars?.coCreationScore || 0}/10
            </div>
            <p className="text-xs text-gray-600 mt-1">Menneskelig bidrag til beslutninger</p>
          </Card>
          <Card title="Active Challenges">
            <div className="text-3xl font-bold text-gray-900">{challenges.length}</div>
            <p className="text-xs text-gray-600 mt-1">Læringsloop-tokens</p>
          </Card>
          <Card title="Unresolved Conflicts">
            <div className="text-3xl font-bold text-gray-900">
              {contradictions.filter((c) => c.status === "unresolved").length}
            </div>
            <p className="text-xs text-gray-600 mt-1">Krever menneskelig intuisjon</p>
          </Card>
          <Card title="Memory Events">
            <div className="text-3xl font-bold text-gray-900">{memories.length}</div>
            <p className="text-xs text-gray-600 mt-1">Episodisk konsekvensminne</p>
          </Card>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 border-b border-gray-200">
          {[
            { key: "pillars", label: "Decision Pillars" },
            { key: "challenges", label: "Challenge Protocol" },
            { key: "contradictions", label: "Contradictions" },
            { key: "memory", label: "Memory" },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as typeof activeTab)}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === tab.key
                  ? "border-b-2 border-blue-500 text-blue-600"
                  : "text-gray-500 hover:text-gray-700"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Decision Pillars Tab */}
        {activeTab === "pillars" && pillars && (
          <div className="space-y-4">
            <Card title="Symbiotic Decision Pillars">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Reality */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-blue-500">📋</span> Reality (Fakta)
                  </h4>
                  <ul className="space-y-1">
                    {pillars.reality.facts.map((fact, i) => (
                      <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
                        <span className="text-gray-400">•</span>
                        {fact}
                      </li>
                    ))}
                  </ul>
                  {pillars.reality.sources && (
                    <div className="text-xs text-gray-500 mt-2">
                      Kilder: {pillars.reality.sources.join(", ")}
                    </div>
                  )}
                </div>

                {/* Interpretation */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-green-500">💡</span> Interpretation (Betydning)
                  </h4>
                  <p className="text-sm text-gray-600">{pillars.interpretation.operational}</p>
                  <p className="text-sm text-gray-600 italic">{pillars.interpretation.whyThisMatters}</p>
                </div>

                {/* Uncertainty */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-yellow-500">❓</span> Uncertainty (Usikkerhet)
                  </h4>
                  <div className="flex items-center gap-2">
                    <Badge color={pillars.uncertainty.confidenceScore > 0.7 ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"}>
                      Konfidens: {(pillars.uncertainty.confidenceScore * 100).toFixed(0)}%
                    </Badge>
                    {pillars.uncertainty.requiresHumanIntuition && (
                      <Badge color="bg-purple-100 text-purple-800">Krever intuisjon</Badge>
                    )}
                  </div>
                  <p className="text-xs text-gray-500">
                    Unknowns: {pillars.uncertainty.unknowns.join(", ")}
                  </p>
                </div>

                {/* Stakes */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-red-500">⚠️</span> Stakes (Risiko)
                  </h4>
                  <Badge color={getRiskColor(pillars.stakes.riskLevel)}>
                    {pillars.stakes.riskLevel.toUpperCase()}
                  </Badge>
                  <p className="text-sm text-gray-600">{pillars.stakes.description}</p>
                </div>

                {/* Choices */}
                <div className="space-y-2 md:col-span-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-indigo-500">🎯</span> Choices (Valg)
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {["choiceA", "choiceB", "choiceC"].map((key, i) => {
                      const choice = pillars.choices[key as keyof typeof pillars.choices];
                      const isRecommended = pillars.recommendation.recommendedChoice === ["A", "B", "C"][i];
                      return (
                        <div
                          key={key}
                          className={`p-3 rounded-lg border ${
                            isRecommended
                              ? "border-green-300 bg-green-50"
                              : "border-gray-200 bg-gray-50"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-medium text-sm">Valg {["A", "B", "C"][i]}</span>
                            {isRecommended && (
                              <Badge color="bg-green-100 text-green-800">Anbefalt</Badge>
                            )}
                          </div>
                          <p className="text-sm font-medium text-gray-900">{choice.label}</p>
                          <p className="text-xs text-gray-600 mt-1">{choice.action}</p>
                          <p className="text-xs text-gray-500 mt-1">→ {choice.expectedOutcome}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Reversibility */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-teal-500">🔄</span> Reversibility (Angrepunkt)
                  </h4>
                  <div className="text-sm">
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-teal-500 h-2 rounded-full"
                          style={{ width: `${pillars.reversibility.score * 100}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">{(pillars.reversibility.score * 100).toFixed(0)}%</span>
                    </div>
                    {pillars.reversibility.rollbackStrategy && (
                      <p className="text-xs text-gray-600 mt-2">
                        Strategi: {pillars.reversibility.rollbackStrategy}
                      </p>
                    )}
                  </div>
                </div>

                {/* Co-Creation Score */}
                <div className="space-y-2">
                  <h4 className="font-semibold text-gray-900 flex items-center gap-2">
                    <span className="text-purple-500">🤝</span> Co-Creation Score
                  </h4>
                  <Badge color={getCoCreationColor(pillars.coCreationScore)}>
                    {pillars.coCreationScore}/10
                  </Badge>
                  <p className="text-xs text-gray-600">
                    {pillars.coCreationScore >= 7
                      ? "Høyt menneskelig bidrag"
                      : pillars.coCreationScore >= 4
                      ? "Moderat samskapelse"
                      : "Primært AI-generert"}
                  </p>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Challenges Tab */}
        {activeTab === "challenges" && (
          <div className="space-y-4">
            <Card title="Submit Challenge">
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Original AI Output
                  </label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows={3}
                    value={challengeForm.original}
                    onChange={(e) =>
                      setChallengeForm({ ...challengeForm, original: e.target.value })
                    }
                    placeholder="Lim inn AI-output som skal utfordres..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Din korrigering/utfordring
                  </label>
                  <textarea
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    rows={3}
                    value={challengeForm.challenge}
                    onChange={(e) =>
                      setChallengeForm({ ...challengeForm, challenge: e.target.value })
                    }
                    placeholder="Din tilbakemelding..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                    value={challengeForm.type}
                    onChange={(e) =>
                      setChallengeForm({ ...challengeForm, type: e.target.value })
                    }
                  >
                    <option value="correct">Correct (Korriger faktisk feil)</option>
                    <option value="expand">Expand (Be om utdypning)</option>
                    <option value="redirect">Redirect (Endre retning)</option>
                    <option value="reject">Reject (Avvis helt)</option>
                  </select>
                </div>
                <Button onClick={handleSubmitChallenge}>Submit Challenge</Button>
              </div>
            </Card>

            <Card title="Challenge History">
              {challenges.length === 0 ? (
                <p className="text-gray-500 text-center py-4">Ingen challenges ennå</p>
              ) : (
                <div className="space-y-3">
                  {challenges.map((c) => (
                    <div key={c.id} className="border rounded-lg p-3 bg-gray-50">
                      <div className="flex items-center justify-between">
                        <Badge color="bg-blue-100 text-blue-800">{c.challengeType}</Badge>
                        <span className="text-xs text-gray-500">
                          Vekt: {c.weight.toFixed(2)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mt-2">{c.humanChallenge}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(c.timestamp).toLocaleString("no-NO")}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Contradictions Tab */}
        {activeTab === "contradictions" && (
          <div className="space-y-4">
            <Card title="Contradiction Surface">
              {contradictions.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  Ingen konflikter oppdaget. Bruk API-et for å sjekke kilder.
                </p>
              ) : (
                <div className="space-y-3">
                  {contradictions.map((c) => (
                    <div key={c.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <Badge
                          color={
                            c.status === "unresolved"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-green-100 text-green-800"
                          }
                        >
                          {c.status}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          Score: {(c.contradictionScore * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                        <div className="bg-red-50 p-2 rounded">
                          <span className="text-xs text-red-600 font-medium">A:</span>
                          <p className="text-gray-700">{c.sourceA.substring(0, 100)}...</p>
                        </div>
                        <div className="bg-blue-50 p-2 rounded">
                          <span className="text-xs text-blue-600 font-medium">B:</span>
                          <p className="text-gray-700">{c.sourceB.substring(0, 100)}...</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}

        {/* Memory Tab */}
        {activeTab === "memory" && (
          <div className="space-y-4">
            <Card title="Memory of Consequence">
              {memories.length === 0 ? (
                <p className="text-gray-500 text-center py-4">
                  Ingen memory events ennå. Disse bygges opp fra challenges over tid.
                </p>
              ) : (
                <div className="space-y-3">
                  {memories.map((m) => (
                    <div key={m.id} className="border rounded-lg p-3 bg-gradient-to-r from-purple-50 to-transparent">
                      <div className="flex items-center justify-between mb-2">
                        <Badge color="bg-purple-100 text-purple-800">
                          Score: {m.importanceScore.toFixed(2)}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          TTL: {m.ttlDays} dager
                        </span>
                      </div>
                      <p className="text-sm font-medium text-gray-900">{m.event}</p>
                      <p className="text-sm text-gray-600">→ {m.outcome}</p>
                      <p className="text-xs text-gray-400 mt-1">
                        {new Date(m.occurredAt).toLocaleString("no-NO")}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
