import type { EchobotLead, RoadmapMissionPayload, RoadmapSyncPreview } from "@roadmap/operator-contracts";

export function leadToMissionPayload(
  lead: EchobotLead,
  operatorNotes?: string
): RoadmapMissionPayload {
  return {
    missionTitle: `Echobot: ${lead.companyName}`,
    origin: "echobot",
    proofDefinition: {
      description: lead.hypothesis,
      requiredArtifacts: lead.evidenceUrl ? [lead.evidenceUrl] : undefined,
    },
    operatorNotes,
    nextActions: [
      "Send personalized outreach email",
      "Schedule discovery call",
      "Capture proof of value delivery",
    ],
    metadata: {
      domain: lead.domain,
      contactEmail: lead.contactEmail,
      confidenceScore: lead.confidenceScore,
    },
  };
}

export function createSyncPreview(
  lead: EchobotLead,
  operatorNotes?: string
): RoadmapSyncPreview {
  return {
    lead,
    payload: leadToMissionPayload(lead, operatorNotes),
  };
}

export function mapSentimentToBadge(sentiment?: string): {
  label: string;
  color: string;
} {
  switch (sentiment) {
    case "positive":
      return { label: "Positive", color: "bg-green-100 text-green-800" };
    case "negative":
      return { label: "Negative", color: "bg-red-100 text-red-800" };
    case "neutral":
      return { label: "Neutral", color: "bg-gray-100 text-gray-800" };
    default:
      return { label: "Unknown", color: "bg-yellow-100 text-yellow-800" };
  }
}

export function mapTruthStatusToBadge(status: string): {
  label: string;
  color: string;
} {
  switch (status) {
    case "PASSED":
      return { label: "Passed", color: "bg-green-100 text-green-800" };
    case "FAILED":
      return { label: "Failed", color: "bg-red-100 text-red-800" };
    case "PENDING":
      return { label: "Pending", color: "bg-yellow-100 text-yellow-800" };
    default:
      return { label: "Unknown", color: "bg-gray-100 text-gray-800" };
  }
}

export function mapSendStatusToBadge(status: string): {
  label: string;
  color: string;
} {
  switch (status) {
    case "SENT":
      return { label: "Sent", color: "bg-blue-100 text-blue-800" };
    case "APPROVED":
      return { label: "Approved", color: "bg-green-100 text-green-800" };
    case "REJECTED":
      return { label: "Rejected", color: "bg-red-100 text-red-800" };
    case "QUEUE":
      return { label: "Queue", color: "bg-gray-100 text-gray-800" };
    default:
      return { label: "Unknown", color: "bg-yellow-100 text-yellow-800" };
  }
}
