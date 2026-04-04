import type { EchobotLead, EchobotStats, EchobotPolicy, RoadmapSyncPreview } from "@roadmap/operator-contracts";

const API_BASE = "/api/echobot";

export async function fetchStats(): Promise<EchobotStats | null> {
  try {
    const res = await fetch(`${API_BASE}/stats`);
    if (!res.ok) throw new Error("Failed to fetch stats");
    return res.json();
  } catch {
    return null;
  }
}

export async function fetchReviewQueue(): Promise<EchobotLead[]> {
  try {
    const res = await fetch(`${API_BASE}/review`);
    if (!res.ok) throw new Error("Failed to fetch review queue");
    return res.json();
  } catch {
    return [];
  }
}

export async function approveLead(
  leadId: string,
  notes?: string
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ leadId, action: "approve", notes }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function rejectLead(
  leadId: string,
  notes?: string
): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/review`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ leadId, action: "reject", notes }),
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function fetchSyncPreview(leadId: string): Promise<RoadmapSyncPreview | null> {
  try {
    const res = await fetch(`${API_BASE}/sync?leadId=${leadId}&preview=true`);
    if (!res.ok) throw new Error("Failed to fetch sync preview");
    return res.json();
  } catch {
    return null;
  }
}

export async function syncToMission(leadId: string): Promise<unknown | null> {
  try {
    const res = await fetch(`${API_BASE}/sync`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ leadId }),
    });
    if (!res.ok) throw new Error("Failed to sync");
    return res.json();
  } catch {
    return null;
  }
}

export function getPolicy(): EchobotPolicy {
  return {
    maxCohortSize: 300,
    manualApprovalRequired: true,
    requiresProofDefinition: true,
    syncRequiresPositiveSignal: true,
  };
}
