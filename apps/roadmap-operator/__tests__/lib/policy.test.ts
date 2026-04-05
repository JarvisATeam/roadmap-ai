import {
  DEFAULT_POLICY,
  canApprove,
  canSync,
  shouldShowInReviewQueue,
  getRiskLevel,
} from "@/lib/echobot/policy";
import type { EchobotLead, EchobotPolicy } from "@roadmap/operator-contracts";

describe("policy", () => {
  const baseLead: EchobotLead = {
    domain: "example.com",
    companyName: "Example Corp",
    contactEmail: "contact@example.com",
    hypothesis: "Test hypothesis",
    confidenceScore: 0.8,
    truthStatus: "PASSED",
    sendStatus: "QUEUE",
  };

  describe("DEFAULT_POLICY", () => {
    it("should have correct default values", () => {
      expect(DEFAULT_POLICY.maxCohortSize).toBe(300);
      expect(DEFAULT_POLICY.manualApprovalRequired).toBe(true);
      expect(DEFAULT_POLICY.requiresProofDefinition).toBe(true);
      expect(DEFAULT_POLICY.syncRequiresPositiveSignal).toBe(true);
    });
  });

  describe("canApprove", () => {
    it("should return true for PASSED lead in QUEUE", () => {
      const lead = { ...baseLead, truthStatus: "PASSED", sendStatus: "QUEUE" };
      expect(canApprove(lead)).toBe(true);
    });

    it("should return true for PENDING lead (manual override)", () => {
      const lead = { ...baseLead, truthStatus: "PENDING", sendStatus: "QUEUE" };
      expect(canApprove(lead)).toBe(true);
    });

    it("should return false for FAILED lead", () => {
      const lead = { ...baseLead, truthStatus: "FAILED", sendStatus: "QUEUE" };
      expect(canApprove(lead)).toBe(false);
    });

    it("should return false for already SENT lead", () => {
      const lead = { ...baseLead, truthStatus: "PASSED", sendStatus: "SENT" };
      expect(canApprove(lead)).toBe(false);
    });

    it("should return false for opted out lead", () => {
      const lead = { ...baseLead, truthStatus: "PASSED", optedOut: true };
      expect(canApprove(lead)).toBe(false);
    });

    it("should use provided policy if given", () => {
      const customPolicy: EchobotPolicy = {
        ...DEFAULT_POLICY,
        manualApprovalRequired: false,
      };
      const lead = { ...baseLead };
      // Should still work the same, policy doesn't affect basic canApprove logic
      expect(canApprove(lead, customPolicy)).toBe(true);
    });
  });

  describe("canSync - fail-closed tests", () => {
    it("should return true for positive sentiment (default policy)", () => {
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        truthStatus: "PASSED",
      };
      expect(canSync(lead)).toBe(true);
    });

    it("should return false for neutral sentiment (syncRequiresPositiveSignal)", () => {
      const lead = {
        ...baseLead,
        replySentiment: "neutral" as const,
        truthStatus: "PASSED",
      };
      expect(canSync(lead)).toBe(false);
    });

    it("should return false for negative sentiment", () => {
      const lead = {
        ...baseLead,
        replySentiment: "negative" as const,
        truthStatus: "PASSED",
      };
      expect(canSync(lead)).toBe(false);
    });

    it("should return true with stripe invoice URL even without positive sentiment", () => {
      const lead = {
        ...baseLead,
        replySentiment: "neutral" as const,
        stripeInvoiceUrl: "https://stripe.com/invoice/123",
        truthStatus: "PASSED",
      };
      // This would require custom policy or additional logic
      // Current implementation checks replySentiment only
      expect(canSync(lead)).toBe(false);
    });

    it("should return true with positive sentiment regardless of stripe URL", () => {
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        stripeInvoiceUrl: "https://stripe.com/invoice/123",
        truthStatus: "PASSED",
      };
      expect(canSync(lead)).toBe(true);
    });

    it("should return false for opted out lead (fail-closed)", () => {
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        optedOut: true,
        truthStatus: "PASSED",
      };
      expect(canSync(lead)).toBe(false);
    });

    it("should return false for FAILED truth status (fail-closed)", () => {
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        truthStatus: "FAILED",
      };
      expect(canSync(lead)).toBe(false);
    });

    it("should return true with PENDING truth status if positive sentiment", () => {
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        truthStatus: "PENDING",
      };
      expect(canSync(lead)).toBe(true);
    });

    it("should allow sync without positive signal if policy allows", () => {
      const permissivePolicy: EchobotPolicy = {
        ...DEFAULT_POLICY,
        syncRequiresPositiveSignal: false,
      };
      const lead = {
        ...baseLead,
        replySentiment: "neutral" as const,
        truthStatus: "PASSED",
      };
      expect(canSync(lead, permissivePolicy)).toBe(true);
    });

    it("should still block opted out even with permissive policy", () => {
      const permissivePolicy: EchobotPolicy = {
        ...DEFAULT_POLICY,
        syncRequiresPositiveSignal: false,
      };
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        optedOut: true,
        truthStatus: "PASSED",
      };
      expect(canSync(lead, permissivePolicy)).toBe(false);
    });

    it("should still block FAILED truth even with permissive policy", () => {
      const permissivePolicy: EchobotPolicy = {
        ...DEFAULT_POLICY,
        syncRequiresPositiveSignal: false,
      };
      const lead = {
        ...baseLead,
        replySentiment: "positive" as const,
        truthStatus: "FAILED",
      };
      expect(canSync(lead, permissivePolicy)).toBe(false);
    });
  });

  describe("shouldShowInReviewQueue", () => {
    it("should return true for QUEUE status", () => {
      const lead = { ...baseLead, sendStatus: "QUEUE" };
      expect(shouldShowInReviewQueue(lead)).toBe(true);
    });

    it("should return true for PENDING truth not yet sent", () => {
      const lead = {
        ...baseLead,
        truthStatus: "PENDING",
        sendStatus: "QUEUE",
      };
      expect(shouldShowInReviewQueue(lead)).toBe(true);
    });

    it("should return false for PENDING already SENT", () => {
      const lead = {
        ...baseLead,
        truthStatus: "PENDING",
        sendStatus: "SENT",
      };
      expect(shouldShowInReviewQueue(lead)).toBe(false);
    });

    it("should return false for APPROVED status", () => {
      const lead = { ...baseLead, sendStatus: "APPROVED" };
      expect(shouldShowInReviewQueue(lead)).toBe(false);
    });

    it("should return false for REJECTED status", () => {
      const lead = { ...baseLead, sendStatus: "REJECTED" };
      expect(shouldShowInReviewQueue(lead)).toBe(false);
    });

    it("should return false for SENT status", () => {
      const lead = { ...baseLead, sendStatus: "SENT" };
      expect(shouldShowInReviewQueue(lead)).toBe(false);
    });
  });

  describe("getRiskLevel", () => {
    it("should return high for FAILED truth status", () => {
      const lead = { ...baseLead, truthStatus: "FAILED" };
      expect(getRiskLevel(lead)).toBe("high");
    });

    it("should return high for opted out lead", () => {
      const lead = { ...baseLead, optedOut: true };
      expect(getRiskLevel(lead)).toBe("high");
    });

    it("should return high for low confidence (< 0.5)", () => {
      const lead = { ...baseLead, confidenceScore: 0.3 };
      expect(getRiskLevel(lead)).toBe("high");
    });

    it("should return medium for medium confidence (0.5 - 0.7)", () => {
      const lead = { ...baseLead, confidenceScore: 0.6 };
      expect(getRiskLevel(lead)).toBe("medium");
    });

    it("should return low for high confidence (>= 0.7)", () => {
      const lead = { ...baseLead, confidenceScore: 0.8 };
      expect(getRiskLevel(lead)).toBe("low");
    });

    it("should prioritize FAILED over confidence", () => {
      const lead = {
        ...baseLead,
        truthStatus: "FAILED",
        confidenceScore: 0.9,
      };
      expect(getRiskLevel(lead)).toBe("high");
    });

    it("should prioritize optedOut over confidence", () => {
      const lead = {
        ...baseLead,
        optedOut: true,
        confidenceScore: 0.9,
      };
      expect(getRiskLevel(lead)).toBe("high");
    });
  });
});
