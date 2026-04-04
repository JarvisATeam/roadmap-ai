"use client";

import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  fetchStats,
  fetchReviewQueue,
  approveLead,
  rejectLead,
  fetchSyncPreview,
} from "@/lib/echobot/client";
import {
  mapTruthStatusToBadge,
  mapSendStatusToBadge,
  mapSentimentToBadge,
} from "@/lib/echobot/mapper";
import { canApprove, canSync, getRiskLevel } from "@/lib/echobot/policy";
import type { EchobotLead, EchobotStats, RoadmapSyncPreview } from "@roadmap/operator-contracts";

export default function EchobotOperatorPage() {
  const [stats, setStats] = useState<EchobotStats | null>(null);
  const [queue, setQueue] = useState<EchobotLead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<EchobotLead | null>(null);
  const [syncPreview, setSyncPreview] = useState<RoadmapSyncPreview | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [statsData, queueData] = await Promise.all([
        fetchStats(),
        fetchReviewQueue(),
      ]);
      setStats(statsData);
      setQueue(queueData);
    } catch {
      setError("Failed to load data");
    } finally {
      setLoading(false);
    }
  }

  async function handleApprove(lead: EchobotLead) {
    const success = await approveLead(lead.id || "", "Approved by operator");
    if (success) {
      await loadData();
    }
  }

  async function handleReject(lead: EchobotLead) {
    const success = await rejectLead(lead.id || "", "Rejected by operator");
    if (success) {
      await loadData();
    }
  }

  async function handleViewSync(lead: EchobotLead) {
    setSelectedLead(lead);
    const preview = await fetchSyncPreview(lead.id || "");
    setSyncPreview(preview);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Echobot Operator</h1>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-gray-900">Echobot Operator</h1>
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
            <Button onClick={loadData} className="mt-2">
              Retry
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">Echobot Operator</h1>
          <Button onClick={loadData} variant="secondary" size="sm">
            Refresh
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card title="Total Leads">
            <div className="text-3xl font-bold text-gray-900">
              {stats?.total || 0}
            </div>
          </Card>
          <Card title="Reply Rate">
            <div className="text-3xl font-bold text-gray-900">
              {((stats?.replyRate || 0) * 100).toFixed(1)}%
            </div>
          </Card>
          <Card title="Positive Rate">
            <div className="text-3xl font-bold text-gray-900">
              {((stats?.positiveRate || 0) * 100).toFixed(1)}%
            </div>
          </Card>
          <Card title="Queue Size">
            <div className="text-3xl font-bold text-gray-900">
              {stats?.queueSize || 0}
            </div>
          </Card>
        </div>

        <Card title="Review Queue">
          {queue.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No leads waiting for review
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Company
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Domain
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Truth
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Confidence
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Reply
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {queue.map((lead) => {
                    const truthBadge = mapTruthStatusToBadge(lead.truthStatus);
                    const sendBadge = mapSendStatusToBadge(lead.sendStatus);
                    const sentimentBadge = mapSentimentToBadge(lead.replySentiment);
                    const riskLevel = getRiskLevel(lead);
                    const canApp = canApprove(lead);
                    const canSyn = canSync(lead);

                    return (
                      <tr
                        key={lead.id}
                        className={lead.optedOut ? "bg-gray-50" : ""}
                      >
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {lead.companyName}
                          {lead.optedOut && (
                            <Badge color="bg-gray-200 text-gray-600">
                              Opted Out
                            </Badge>
                          )}
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {lead.domain}
                        </td>
                        <td className="px-4 py-3">
                          <Badge color={truthBadge.color}>{truthBadge.label}</Badge>
                        </td>
                        <td className="px-4 py-3 text-sm text-gray-900">
                          {(lead.confidenceScore * 100).toFixed(0)}%
                        </td>
                        <td className="px-4 py-3">
                          <Badge color={sendBadge.color}>{sendBadge.label}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <Badge color={sentimentBadge.color}>
                            {sentimentBadge.label}
                          </Badge>
                        </td>
                        <td className="px-4 py-3 space-x-2">
                          {canApp && (
                            <>
                              <Button
                                size="sm"
                                onClick={() => handleApprove(lead)}
                              >
                                Approve
                              </Button>
                              <Button
                                size="sm"
                                variant="danger"
                                onClick={() => handleReject(lead)}
                              >
                                Reject
                              </Button>
                            </>
                          )}
                          {canSyn && (
                            <Button
                              size="sm"
                              variant="secondary"
                              onClick={() => handleViewSync(lead)}
                            >
                              Sync
                            </Button>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        {selectedLead && syncPreview && (
          <Card title="Sync Preview">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700">
                  Mission Title
                </h4>
                <p className="mt-1 text-sm text-gray-900">
                  {(syncPreview as { payload?: { missionTitle?: string } }).payload?.missionTitle}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-700">
                  Proof Definition
                </h4>
                <p className="mt-1 text-sm text-gray-900">
                  {(syncPreview as { payload?: { proofDefinition?: { description?: string } } }).payload?.proofDefinition?.description}
                </p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-700">
                  Next Actions
                </h4>
                <ul className="mt-1 list-disc list-inside text-sm text-gray-900">
                  {((syncPreview as { payload?: { nextActions?: string[] } }).payload?.nextActions || []).map((action, i) => (
                    <li key={i}>{action}</li>
                  ))}
                </ul>
              </div>
              <div className="flex gap-2">
                <Button onClick={() => setSelectedLead(null)} variant="secondary">
                  Close
                </Button>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
