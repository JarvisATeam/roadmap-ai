/**
 * Tests for Symbiosis Memory Module
 */

import {
  MemoryManager,
  memoryStore,
  formatMemory,
} from "@/lib/symbiosis/memory";
import type { SymbioticChallengeToken, ChallengeType } from "@roadmap/operator-contracts";

describe("MemoryStore", () => {
  beforeEach(() => {
    memoryStore.clear();
  });

  describe("save", () => {
    it("should save event with calculated importance score", () => {
      const event = memoryStore.save({
        event: "Test hendelse",
        outcome: "Test utfall",
        outcomeMagnitude: 0.8,
        humanFeedback: {
          feltStress: 0.3,
          feltHope: 0.7,
          feltRegret: 0.1,
          empathyIndex: 0.6,
        },
        affectedHumans: 2,
        occurredAt: new Date().toISOString(),
      });

      expect(event.id).toBeDefined();
      expect(event.importanceScore).toBeGreaterThan(0);
      expect(event.ttlDays).toBeGreaterThan(0);
    });

    it("should calculate higher score for high emotional resonance", () => {
      const lowEmotion = memoryStore.save({
        event: "Low emotion",
        outcome: "Outcome",
        outcomeMagnitude: 0.5,
        humanFeedback: {
          feltStress: 0.1,
          feltHope: 0.1,
          feltRegret: 0.1,
        },
        affectedHumans: 1,
        occurredAt: new Date().toISOString(),
      });

      const highEmotion = memoryStore.save({
        event: "High emotion",
        outcome: "Outcome",
        outcomeMagnitude: 0.5,
        humanFeedback: {
          feltStress: 0.8,
          feltHope: 0.9,
          feltRegret: 0.7,
        },
        affectedHumans: 1,
        occurredAt: new Date().toISOString(),
      });

      expect(highEmotion.importanceScore).toBeGreaterThan(lowEmotion.importanceScore);
    });
  });

  describe("getRelevantForContext", () => {
    it("should return relevant memories for context", () => {
      memoryStore.save({
        event: "Kundemøte med Acme Corp",
        outcome: "Positivt",
        outcomeMagnitude: 0.8,
        humanFeedback: {},
        affectedHumans: 3,
        occurredAt: new Date().toISOString(),
      });

      memoryStore.save({
        event: "Teknisk problem med server",
        outcome: "Løst",
        outcomeMagnitude: 0.6,
        humanFeedback: {},
        affectedHumans: 1,
        occurredAt: new Date().toISOString(),
      });

      const relevant = memoryStore.getRelevantForContext("Hvordan gikk møtet med Acme?");
      
      expect(relevant.length).toBeGreaterThan(0);
      expect(relevant[0].event).toContain("Acme");
    });
  });

  describe("prune", () => {
    it("should remove low-importance memories", () => {
      // Lag gammel hendelse med lav score
      memoryStore.save({
        event: "Ugyldig hendelse",
        outcome: "Ingen konsekvens",
        outcomeMagnitude: 0.01,
        humanFeedback: {
          feltStress: 0,
          feltHope: 0,
          feltRegret: 0,
        },
        affectedHumans: 0,
        occurredAt: new Date(Date.now() - 100 * 24 * 60 * 60 * 1000).toISOString(), // 100 dager gammel
      });

      const before = memoryStore.getAll().length;
      const deleted = memoryStore.prune();
      const after = memoryStore.getAll().length;

      expect(deleted).toBeGreaterThan(0);
      expect(after).toBeLessThan(before);
    });
  });
});

describe("MemoryManager", () => {
  let manager: MemoryManager;

  beforeEach(() => {
    memoryStore.clear();
    manager = new MemoryManager();
  });

  describe("recordFromChallenge", () => {
    it("should create memory from challenge token", () => {
      const token: SymbioticChallengeToken = {
        id: "challenge_123",
        originalOutput: "AI sa noe",
        humanChallenge: "Dette var feil",
        challengeType: "correct" as ChallengeType,
        timestamp: new Date().toISOString(),
        weight: 0.7,
      };

      const memory = manager.recordFromChallenge(token, "Korrigert svar", 2);

      expect(memory.event).toContain("Challenge");
      expect(memory.outcome).toBe("Korrigert svar");
      expect(memory.relatedChallengeId).toBe(token.id);
      expect(memory.humanFeedback.feltStress).toBeGreaterThan(0);
    });

    it("should set higher stress for reject challenges", () => {
      const rejectToken: SymbioticChallengeToken = {
        id: "challenge_reject",
        originalOutput: "AI output",
        humanChallenge: "Helt feil",
        challengeType: "reject" as ChallengeType,
        timestamp: new Date().toISOString(),
        weight: 0.9,
      };

      const correctToken: SymbioticChallengeToken = {
        id: "challenge_correct",
        originalOutput: "AI output",
        humanChallenge: "Liten justering",
        challengeType: "correct" as ChallengeType,
        timestamp: new Date().toISOString(),
        weight: 0.6,
      };

      const rejectMemory = manager.recordFromChallenge(rejectToken, "Avvist");
      const correctMemory = manager.recordFromChallenge(correctToken, "Korrigert");

      expect(rejectMemory.humanFeedback.feltStress).toBeGreaterThan(
        correctMemory.humanFeedback.feltStress || 0
      );
    });
  });

  describe("getContextForQuery", () => {
    it("should return formatted context string", () => {
      memoryStore.save({
        event: "Viktig beslutning",
        outcome: "Suksess",
        outcomeMagnitude: 0.9,
        humanFeedback: {},
        affectedHumans: 5,
        occurredAt: new Date().toISOString(),
      });

      const context = manager.getContextForQuery("beslutning");

      expect(context).toContain("Viktig beslutning");
      expect(context).toContain("Suksess");
    });

    it("should return empty string when no relevant memories", () => {
      const context = manager.getContextForQuery("ukjent emne");
      expect(context).toBe("");
    });
  });
});

describe("formatMemory", () => {
  it("should format memory event for display", () => {
    const event = {
      id: "mem_123",
      event: "Viktig hendelse som skjedde",
      outcome: "Suksess",
      outcomeMagnitude: 0.9,
      humanFeedback: {},
      affectedHumans: 3,
      occurredAt: new Date().toISOString(),
      importanceScore: 0.75,
      ttlDays: 30,
    };

    const formatted = formatMemory(event);

    expect(formatted).toContain("Viktig hendelse");
    expect(formatted).toContain("0.75");
  });
});
