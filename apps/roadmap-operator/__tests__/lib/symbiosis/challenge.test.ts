/**
 * Tests for Symbiosis Challenge Module
 */

import {
  ChallengeManager,
  ChallengeConfig,
  challengeStore,
  isChallengeWindowOpen,
  formatChallenge,
} from "@/lib/symbiosis/challenge";
import type { ChallengeType, ChallengeContext } from "@roadmap/operator-contracts";

describe("ChallengeManager", () => {
  let manager: ChallengeManager;

  beforeEach(() => {
    challengeStore.clear();
    manager = new ChallengeManager();
  });

  describe("acceptChallenge", () => {
    it("should create a challenge token with correct structure", () => {
      const token = manager.acceptChallenge(
        "Dette er feil",
        "AI sa at prisen var 100",
        "correct"
      );

      expect(token.id).toBeDefined();
      expect(token.humanChallenge).toBe("Dette er feil");
      expect(token.originalOutput).toBe("AI sa at prisen var 100");
      expect(token.challengeType).toBe("correct");
      expect(token.weight).toBeGreaterThan(0);
      expect(token.timestamp).toBeDefined();
    });

    it("should calculate higher weight for reject type", () => {
      const correctToken = manager.acceptChallenge("x", "y", "correct");
      const rejectToken = manager.acceptChallenge("x", "y", "reject");

      expect(rejectToken.weight).toBeGreaterThan(correctToken.weight);
    });

    it("should calculate higher weight for emotional indicators", () => {
      const normalToken = manager.acceptChallenge("Dette ser bra ut", "y", "correct");
      const emotionalToken = manager.acceptChallenge("Dette er helt feil!", "y", "correct");

      expect(emotionalToken.weight).toBeGreaterThan(normalToken.weight);
    });

    it("should throw when session limit exceeded", () => {
      const config: ChallengeConfig = {
        challengeWindowSeconds: 30,
        minWeightThreshold: 0.1,
        maxChallengesPerSession: 2,
      };
      const limitedManager = new ChallengeManager(config);
      const context: ChallengeContext = { sessionId: "test-session" };

      limitedManager.acceptChallenge("a", "b", "correct", context);
      limitedManager.acceptChallenge("c", "d", "correct", context);

      expect(() => {
        limitedManager.acceptChallenge("e", "f", "correct", context);
      }).toThrow("Challenge limit exceeded");
    });
  });

  describe("handleChallengeRequest", () => {
    it("should return success for valid request", () => {
      const result = manager.handleChallengeRequest({
        originalOutput: "AI output",
        humanChallenge: "Menneskelig korrigering",
        challengeType: "correct",
      });

      expect(result.success).toBe(true);
      expect(result.token).toBeDefined();
    });

    it("should return error for missing fields", () => {
      const result = manager.handleChallengeRequest({
        originalOutput: "",
        humanChallenge: "test",
        challengeType: "correct",
      });

      expect(result.success).toBe(false);
      expect(result.error).toBeDefined();
    });
  });

  describe("verifyChallenge", () => {
    it("should update verification status", () => {
      const token = manager.acceptChallenge("x", "y", "correct");
      
      const result = manager.verifyChallenge(token.id, "manual");
      
      expect(result).toBe(true);
      const stored = challengeStore.get(token.id);
      expect(stored?.verificationStatus?.status).toBe("verified");
      expect(stored?.verificationStatus?.method).toBe("manual");
    });

    it("should return false for non-existent token", () => {
      const result = manager.verifyChallenge("non-existent", "manual");
      expect(result).toBe(false);
    });
  });

  describe("getChallengesForLearning", () => {
    it("should only return verified challenges", () => {
      const token1 = manager.acceptChallenge("x", "y", "correct");
      const token2 = manager.acceptChallenge("a", "b", "correct");
      
      manager.verifyChallenge(token1.id, "auto");

      const learningChallenges = manager.getChallengesForLearning();
      
      expect(learningChallenges).toHaveLength(1);
      expect(learningChallenges[0].id).toBe(token1.id);
    });
  });
});

describe("isChallengeWindowOpen", () => {
  it("should return true for recent output", () => {
    const recent = new Date().toISOString();
    expect(isChallengeWindowOpen(recent, 30)).toBe(true);
  });

  it("should return false for old output", () => {
    const old = new Date(Date.now() - 60000).toISOString();
    expect(isChallengeWindowOpen(old, 30)).toBe(false);
  });
});

describe("formatChallenge", () => {
  it("should format token for display", () => {
    const token = {
      id: "test",
      originalOutput: "AI output",
      humanChallenge: "Menneskelig input",
      challengeType: "correct" as ChallengeType,
      timestamp: new Date().toISOString(),
      weight: 0.75,
    };

    const formatted = formatChallenge(token);
    
    expect(formatted).toContain("CORRECT");
    expect(formatted).toContain("0.75");
    expect(formatted).toContain("Menneskelig input");
  });
});
