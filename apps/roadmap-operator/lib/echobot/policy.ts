import type { EchobotLead, EchobotPolicy } from "@roadmap/operator-contracts";

export const DEFAULT_POLICY: EchobotPolicy = {
  maxCohortSize: 300,
  manualApprovalRequired: true,
  requiresProofDefinition: true,
  syncRequiresPositiveSignal: true,
};

export function canApprove(lead: EchobotLead, policy?: EchobotPolicy): boolean {
  const p = policy || DEFAULT_POLICY;
  
  // Cannot approve if already sent
  if (lead.sendStatus === "SENT") return false;
  
  // Cannot approve if opted out
  if (lead.optedOut) return false;
  
  // Cannot approve if truth check failed
  if (lead.truthStatus === "FAILED") return false;
  
  // Can approve if passed or pending (manual override)
  return lead.truthStatus === "PASSED" || lead.truthStatus === "PENDING";
}

export function canSync(lead: EchobotLead, policy?: EchobotPolicy): boolean {
  const p = policy || DEFAULT_POLICY;
  
  // Requires positive signal if policy says so
  if (p.syncRequiresPositiveSignal && lead.replySentiment !== "positive") {
    return false;
  }
  
  // Cannot sync if opted out
  if (lead.optedOut) return false;
  
  // Cannot sync if truth check failed
  if (lead.truthStatus === "FAILED") return false;
  
  return true;
}

export function shouldShowInReviewQueue(lead: EchobotLead): boolean {
  // Show leads that are waiting for approval
  if (lead.sendStatus === "QUEUE") return true;
  
  // Show leads that need manual review
  if (lead.truthStatus === "PENDING" && lead.sendStatus !== "SENT") return true;
  
  return false;
}

export function getRiskLevel(lead: EchobotLead): "low" | "medium" | "high" {
  if (lead.truthStatus === "FAILED" || lead.optedOut) return "high";
  if (lead.confidenceScore < 0.5) return "high";
  if (lead.confidenceScore < 0.7) return "medium";
  return "low";
}
