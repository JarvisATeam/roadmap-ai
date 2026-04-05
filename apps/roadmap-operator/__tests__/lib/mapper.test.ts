import {
  leadToMissionPayload,
  createSyncPreview,
  mapSentimentToBadge,
  mapTruthStatusToBadge,
  mapSendStatusToBadge,
} from "@/lib/echobot/mapper";
import type { EchobotLead } from "@roadmap/operator-contracts";

describe("mapper", () => {
  const mockLead: EchobotLead = {
    id: "lead-123",
    domain: "example.com",
    companyName: "Example Corp",
    contactEmail: "contact@example.com",
    contactName: "John Doe",
    hypothesis: "Company needs better infrastructure",
    hookType: "timeline-compression",
    compressedTimeline: "14 days vs 6 months",
    draftSubject: "Migration timeline",
    draftBody: "We can help you migrate...",
    evidenceUrl: "https://firecrawl.io/evidence/123",
    confidenceScore: 0.85,
    truthStatus: "PASSED",
    sendStatus: "QUEUE",
    replySentiment: "positive",
    createdAt: "2026-04-05T00:00:00Z",
  };

  describe("leadToMissionPayload", () => {
    it("should create mission payload from lead", () => {
      const payload = leadToMissionPayload(mockLead);

      expect(payload.missionTitle).toBe("Echobot: Example Corp");
      expect(payload.origin).toBe("echobot");
      expect(payload.proofDefinition.description).toBe(mockLead.hypothesis);
      expect(payload.proofDefinition.requiredArtifacts).toEqual([
        mockLead.evidenceUrl,
      ]);
    });

    it("should include operator notes when provided", () => {
      const notes = "Important lead, prioritize";
      const payload = leadToMissionPayload(mockLead, notes);

      expect(payload.operatorNotes).toBe(notes);
    });

    it("should handle lead without evidence URL", () => {
      const leadWithoutEvidence = { ...mockLead, evidenceUrl: undefined };
      const payload = leadToMissionPayload(leadWithoutEvidence);

      expect(payload.proofDefinition.requiredArtifacts).toBeUndefined();
    });

    it("should have required next actions", () => {
      const payload = leadToMissionPayload(mockLead);

      expect(payload.nextActions).toHaveLength(3);
      expect(payload.nextActions).toContain("Send personalized outreach email");
      expect(payload.nextActions).toContain("Schedule discovery call");
      expect(payload.nextActions).toContain("Capture proof of value delivery");
    });

    it("should include metadata with domain and contact", () => {
      const payload = leadToMissionPayload(mockLead);

      expect(payload.metadata).toEqual({
        domain: mockLead.domain,
        contactEmail: mockLead.contactEmail,
        confidenceScore: mockLead.confidenceScore,
      });
    });
  });

  describe("createSyncPreview", () => {
    it("should create sync preview with lead and payload", () => {
      const preview = createSyncPreview(mockLead);

      expect(preview.lead).toEqual(mockLead);
      expect(preview.payload.missionTitle).toBe("Echobot: Example Corp");
    });

    it("should include operator notes in preview", () => {
      const notes = "Sync this lead ASAP";
      const preview = createSyncPreview(mockLead, notes);

      expect(preview.payload.operatorNotes).toBe(notes);
    });
  });

  describe("mapSentimentToBadge", () => {
    it("should return green badge for positive sentiment", () => {
      const badge = mapSentimentToBadge("positive");
      expect(badge.label).toBe("Positive");
      expect(badge.color).toContain("green");
    });

    it("should return red badge for negative sentiment", () => {
      const badge = mapSentimentToBadge("negative");
      expect(badge.label).toBe("Negative");
      expect(badge.color).toContain("red");
    });

    it("should return gray badge for neutral sentiment", () => {
      const badge = mapSentimentToBadge("neutral");
      expect(badge.label).toBe("Neutral");
      expect(badge.color).toContain("gray");
    });

    it("should return yellow badge for unknown sentiment", () => {
      const badge = mapSentimentToBadge(undefined);
      expect(badge.label).toBe("Unknown");
      expect(badge.color).toContain("yellow");
    });
  });

  describe("mapTruthStatusToBadge", () => {
    it("should return green badge for PASSED", () => {
      const badge = mapTruthStatusToBadge("PASSED");
      expect(badge.label).toBe("Passed");
      expect(badge.color).toContain("green");
    });

    it("should return red badge for FAILED", () => {
      const badge = mapTruthStatusToBadge("FAILED");
      expect(badge.label).toBe("Failed");
      expect(badge.color).toContain("red");
    });

    it("should return yellow badge for PENDING", () => {
      const badge = mapTruthStatusToBadge("PENDING");
      expect(badge.label).toBe("Pending");
      expect(badge.color).toContain("yellow");
    });

    it("should return gray badge for unknown status", () => {
      const badge = mapTruthStatusToBadge("UNKNOWN");
      expect(badge.label).toBe("Unknown");
      expect(badge.color).toContain("gray");
    });
  });

  describe("mapSendStatusToBadge", () => {
    it("should return blue badge for SENT", () => {
      const badge = mapSendStatusToBadge("SENT");
      expect(badge.label).toBe("Sent");
      expect(badge.color).toContain("blue");
    });

    it("should return green badge for APPROVED", () => {
      const badge = mapSendStatusToBadge("APPROVED");
      expect(badge.label).toBe("Approved");
      expect(badge.color).toContain("green");
    });

    it("should return red badge for REJECTED", () => {
      const badge = mapSendStatusToBadge("REJECTED");
      expect(badge.label).toBe("Rejected");
      expect(badge.color).toContain("red");
    });

    it("should return gray badge for QUEUE", () => {
      const badge = mapSendStatusToBadge("QUEUE");
      expect(badge.label).toBe("Queue");
      expect(badge.color).toContain("gray");
    });

    it("should return yellow badge for unknown status", () => {
      const badge = mapSendStatusToBadge("UNKNOWN");
      expect(badge.label).toBe("Unknown");
      expect(badge.color).toContain("yellow");
    });
  });
});
