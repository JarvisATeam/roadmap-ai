/**
 * Symbiosis Challenge Module
 * 
 * Implementerer Challenge Protocol - mekanismen for menneskelig
 * korrigering av AI-output. Alle challenges logges som tokens
 * for kontinuerlig læring (RLAIF).
 */

import {
  SymbioticChallengeToken,
  ChallengeType,
  ChallengeContext,
  ChallengeCreateRequest,
  ChallengeCreateResponse,
  VerificationStatus,
} from "@roadmap/operator-contracts";

/**
 * Konfigurasjon for challenge-systemet
 */
export interface ChallengeConfig {
  /** Vindu etter output der challenge er mulig (sekunder) */
  challengeWindowSeconds: number;
  
  /** Minimum vekt for å lagre challenge */
  minWeightThreshold: number;
  
  /** Maksimalt antall challenges per sesjon */
  maxChallengesPerSession: number;
}

const DEFAULT_CONFIG: ChallengeConfig = {
  challengeWindowSeconds: 30,
  minWeightThreshold: 0.1,
  maxChallengesPerSession: 100,
};

/**
 * Challenge Store - In-memory storage (kan erstattes med DB)
 */
export class ChallengeStore {
  private challenges: Map<string, SymbioticChallengeToken> = new Map();
  private sessionChallenges: Map<string, number> = new Map();

  save(token: SymbioticChallengeToken): void {
    this.challenges.set(token.id, token);
    
    // Track per session
    const sessionId = token.context?.sessionId || "default";
    const current = this.sessionChallenges.get(sessionId) || 0;
    this.sessionChallenges.set(sessionId, current + 1);
  }

  get(id: string): SymbioticChallengeToken | undefined {
    return this.challenges.get(id);
  }

  getAll(): SymbioticChallengeToken[] {
    return Array.from(this.challenges.values());
  }

  getBySession(sessionId: string): SymbioticChallengeToken[] {
    return this.getAll().filter(c => c.context?.sessionId === sessionId);
  }

  getCountBySession(sessionId: string): number {
    return this.sessionChallenges.get(sessionId) || 0;
  }

  update(id: string, updates: Partial<SymbioticChallengeToken>): boolean {
    const existing = this.challenges.get(id);
    if (!existing) return false;
    
    this.challenges.set(id, { ...existing, ...updates });
    return true;
  }

  clear(): void {
    this.challenges.clear();
    this.sessionChallenges.clear();
  }
}

// Singleton instance
export const challengeStore = new ChallengeStore();

/**
 * Challenge Manager - Hovedklasse for challenge-håndtering
 */
export class ChallengeManager {
  private config: ChallengeConfig;

  constructor(config: Partial<ChallengeConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Aksepterer en challenge fra menneskelig bruker
   */
  acceptChallenge(
    humanInput: string,
    originalOutput: string,
    type: ChallengeType = "correct",
    context?: ChallengeContext
  ): SymbioticChallengeToken {
    const sessionId = context?.sessionId || "default";
    
    // Sjekk sesjonsbegrensning
    const sessionCount = challengeStore.getCountBySession(sessionId);
    if (sessionCount >= this.config.maxChallengesPerSession) {
      throw new Error("Challenge limit exceeded for this session");
    }

    // Beregn vekt basert på input
    const weight = this.calculateWeight(humanInput, type);
    
    // Opprett token
    const token: SymbioticChallengeToken = {
      id: this.generateId(),
      originalOutput,
      humanChallenge: humanInput,
      challengeType: type,
      timestamp: new Date().toISOString(),
      weight,
      context,
      verificationStatus: {
        status: "pending",
      },
    };

    // Lagre
    challengeStore.save(token);

    return token;
  }

  /**
   * Behandler en challenge request fra API
   */
  handleChallengeRequest(request: ChallengeCreateRequest): ChallengeCreateResponse {
    // Validate required fields
    if (!request.originalOutput?.trim()) {
      return {
        success: false,
        error: "Missing required field: originalOutput",
      };
    }
    if (!request.humanChallenge?.trim()) {
      return {
        success: false,
        error: "Missing required field: humanChallenge",
      };
    }

    try {
      const token = this.acceptChallenge(
        request.humanChallenge,
        request.originalOutput,
        request.challengeType,
        request.context
      );

      return {
        success: true,
        token,
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      };
    }
  }

  /**
   * Regenerer output basert på challenge token
   */
  regenerateWithToken(token: SymbioticChallengeToken): string {
    // Dette vil integreres med faktisk AI/LLM i senere faser
    // Nå returnerer vi en placeholder
    return `[Regenerert basert på challenge: ${token.humanChallenge}]`;
  }

  /**
   * Beregner vekt basert på emosjonell intensitet og type
   */
  private calculateWeight(humanInput: string, type: ChallengeType): number {
    let baseWeight = 0.5;

    // Juster basert på type
    switch (type) {
      case "reject":
        baseWeight = 0.9;
        break;
      case "redirect":
        baseWeight = 0.7;
        break;
      case "correct":
        baseWeight = 0.6;
        break;
      case "expand":
        baseWeight = 0.3;
        break;
    }

    // Juster basert på input-lengde (proxy for engasjement)
    const lengthFactor = Math.min(humanInput.length / 100, 1) * 0.2;
    
    // Juster basert på emosjonelle indikatorer
    const emotionalIndicators = [
      "!", "feil", "galt", "viktig", "kritisk", "nei",
      "wrong", "incorrect", "important", "critical", "no"
    ];
    const emotionalFactor = emotionalIndicators.some(ind => 
      humanInput.toLowerCase().includes(ind)
    ) ? 0.3 : 0;

    return Math.min(baseWeight + lengthFactor + emotionalFactor, 1);
  }

  /**
   * Verifiserer en challenge (placeholder for TPM-fremtidig)
   */
  verifyChallenge(tokenId: string, method: "manual" | "auto" = "auto"): boolean {
    const token = challengeStore.get(tokenId);
    if (!token) return false;

    const verification: VerificationStatus = {
      status: "verified",
      method,
      verifiedAt: new Date().toISOString(),
    };

    return challengeStore.update(tokenId, { verificationStatus: verification });
  }

  /**
   * Henter alle challenges for analyse
   */
  getChallengesForLearning(): SymbioticChallengeToken[] {
    return challengeStore.getAll().filter(
      c => c.verificationStatus?.status === "verified"
    );
  }

  /**
   * Genererer unik ID
   */
  private generateId(): string {
    return `challenge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Default manager instance
export const challengeManager = new ChallengeManager();

/**
 * Utility: Sjekker om challenge-vindu fortsatt er åpent
 */
export function isChallengeWindowOpen(
  outputTimestamp: string,
  windowSeconds: number = DEFAULT_CONFIG.challengeWindowSeconds
): boolean {
  const outputTime = new Date(outputTimestamp).getTime();
  const now = Date.now();
  return (now - outputTime) / 1000 <= windowSeconds;
}

/**
 * Utility: Formatter challenge for visning
 */
export function formatChallenge(token: SymbioticChallengeToken): string {
  const date = new Date(token.timestamp).toLocaleString("no-NO");
  return `[${date}] ${token.challengeType.toUpperCase()} (vekt: ${token.weight.toFixed(2)}): ${token.humanChallenge}`;
}
