/**
 * Tests for Symbiosis Decision Module
 */

import {
  DecisionFormatter,
  decisionFormatter,
  handleDecisionRequest,
  formatEchobotReviewToPillars,
} from "@/lib/symbiosis/decision";
import type { EchobotLead, EchobotReviewResult, EchobotTruthStatus } from "@roadmap/operator-contracts";

describe("DecisionFormatter", () => {
  let formatter: DecisionFormatter;

  beforeEach(() => {
    formatter = new DecisionFormatter();
  });

  describe("formatToPillars", () => {
    it("should create pillars from basic input", () => {
      const pillars = formatter.formatToPillars({
        query: "Test query",
      });

      expect(pillars.reality).toBeDefined();
      expect(pillars.interpretation).toBeDefined();
      expect(pillars.uncertainty).toBeDefined();
      expect(pillars.stakes).toBeDefined();
      expect(pillars.choices).toBeDefined();
      expect(pillars.recommendation).toBeDefined();
      expect(pillars.reversibility).toBeDefined();
      expect(pillars.coCreationScore).toBeGreaterThanOrEqual(0);
      expect(pillars.coCreationScore).toBeLessThanOrEqual(10);
    });

    it("should include echobot lead data in reality", () => {
      const lead: EchobotLead = {
        domain: "example.com",
        companyName: "Example AS",
        contactEmail: "test@example.com",
        hypothesis: "Potensiell kunde",
        confidenceScore: 0.85,
        truthStatus: "PASSED" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      };

      const pillars = formatter.formatToPillars({
        query: "Test",
        echobotLead: lead,
      });

      expect(pillars.reality.facts).toContain("Domene: example.com");
      expect(pillars.reality.facts).toContain("Selskap: Example AS");
      expect(pillars.reality.facts).toContain("Sannhetssjekk: Verifisert");
    });

    it("should calculate co-creation score based on input", () => {
      const aiOnly = formatter.formatToPillars({ query: "test" });
      expect(aiOnly.coCreationScore).toBeLessThan(5);

      const withHuman = formatter.formatToPillars({
        query: "test",
        humanInput: "Menneskelig kommentar",
      });
      expect(withHuman.coCreationScore).toBeGreaterThan(aiOnly.coCreationScore);
    });
  });

  describe("uncertainty calculation", () => {
    it("should flag high uncertainty for failed truth check", () => {
      const lead: EchobotLead = {
        domain: "test.com",
        companyName: "Test",
        contactEmail: "test@test.com",
        hypothesis: "Test",
        confidenceScore: 0.5,
        truthStatus: "FAILED" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      };

      const pillars = formatter.formatToPillars({
        query: "test",
        echobotLead: lead,
      });

      expect(pillars.uncertainty.requiresHumanIntuition).toBe(true);
      expect(pillars.uncertainty.confidenceScore).toBeLessThan(0.5);
      expect(pillars.uncertainty.dealbreakers.length).toBeGreaterThan(0);
    });

    it("should require intuition for pending truth status", () => {
      const lead: EchobotLead = {
        domain: "test.com",
        companyName: "Test",
        contactEmail: "test@test.com",
        hypothesis: "Test",
        confidenceScore: 0.8,
        truthStatus: "PENDING" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      };

      const pillars = formatter.formatToPillars({
        query: "test",
        echobotLead: lead,
      });

      expect(pillars.uncertainty.requiresHumanIntuition).toBe(true);
    });
  });

  describe("stakes calculation", () => {
    it("should set high risk for failed truth status", () => {
      const lead: EchobotLead = {
        domain: "test.com",
        companyName: "Test",
        contactEmail: "test@test.com",
        hypothesis: "Test",
        confidenceScore: 0.5,
        truthStatus: "FAILED" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      };

      const pillars = formatter.formatToPillars({
        query: "test",
        echobotLead: lead,
      });

      expect(pillars.stakes.riskLevel).toBe("high");
    });

    it("should set low risk for passed truth status", () => {
      const lead: EchobotLead = {
        domain: "test.com",
        companyName: "Test",
        contactEmail: "test@test.com",
        hypothesis: "Test",
        confidenceScore: 0.9,
        truthStatus: "PASSED" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      };

      const pillars = formatter.formatToPillars({
        query: "test",
        echobotLead: lead,
      });

      expect(pillars.stakes.riskLevel).toBe("low");
    });
  });

  describe("recommendation calculation", () => {
    it("should recommend choice A for approved lead", () => {
      const reviewResult: EchobotReviewResult = {
        lead: {
          domain: "test.com",
          companyName: "Test",
          contactEmail: "test@test.com",
          hypothesis: "Test",
          confidenceScore: 0.9,
          truthStatus: "PASSED" as EchobotTruthStatus,
          sendStatus: "APPROVED",
        },
        truth: {
          status: "PASSED" as EchobotTruthStatus,
          confidenceScore: 0.9,
        },
        approved: true,
      };

      const pillars = formatter.formatToPillars({
        query: "test",
        reviewResult,
      });

      expect(pillars.recommendation.recommendedChoice).toBe("A");
      expect(pillars.recommendation.supportedBy).toBe("human");
    });
  });
});

describe("handleDecisionRequest", () => {
  it("should return success for valid request", () => {
    const result = handleDecisionRequest({
      query: "Test query",
    });

    expect(result.success).toBe(true);
    expect(result.pillars).toBeDefined();
    expect(result.formattedOutput).toBeDefined();
  });

  it("should return error for missing query", () => {
    // @ts-expect-error Testing invalid input
    const result = handleDecisionRequest({});

    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});

describe("formatEchobotReviewToPillars", () => {
  it("should format review result to pillars", () => {
    const reviewResult: EchobotReviewResult = {
      lead: {
        domain: "test.com",
        companyName: "Test AS",
        contactEmail: "test@test.com",
        hypothesis: "Test hypothesis",
        confidenceScore: 0.85,
        truthStatus: "PASSED" as EchobotTruthStatus,
        sendStatus: "QUEUE",
      },
      truth: {
        status: "PASSED" as EchobotTruthStatus,
        confidenceScore: 0.9,
      },
      approved: true,
      reviewerNotes: "Ser bra ut",
    };

    const pillars = formatEchobotReviewToPillars(reviewResult);

    expect(pillars.reality.facts).toContain("Domene: test.com");
    expect(pillars.reality.facts).toContain("Selskap: Test AS");
    expect(pillars.coCreationScore).toBeGreaterThan(5);
  });
});
