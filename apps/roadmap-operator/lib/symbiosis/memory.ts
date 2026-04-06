/**
 * Symbiosis Memory Module
 * 
 * Implementerer "Memory of Consequence" - felles episodisk minne
 * av hendelser og feedback. Inkluderer emotion-weighted TTL.
 */

import {
  ConsequenceMemoryEvent,
  HumanFeedback,
  SymbioticChallengeToken,
} from "@roadmap/operator-contracts";

/**
 * Konfigurasjon for memory-systemet
 */
export interface MemoryConfig {
  /** Standard TTL i dager */
  defaultTTLDays: number;
  /** Threshold for pruning */
  pruneThreshold: number;
  /** Decay rate per dag */
  decayRate: number;
}

const DEFAULT_CONFIG: MemoryConfig = {
  defaultTTLDays: 90,
  pruneThreshold: 0.08,
  decayRate: 0.03,
};

/**
 * Memory Store - In-memory med importance-weighted TTL
 */
export class MemoryStore {
  private memories: Map<string, ConsequenceMemoryEvent> = new Map();
  private config: MemoryConfig;

  constructor(config: Partial<MemoryConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Lagrer en memory event
   */
  save(event: Omit<ConsequenceMemoryEvent, "id" | "importanceScore" | "ttlDays">): ConsequenceMemoryEvent {
    const daysOld = 0; // Ny hendelse
    const importanceScore = this.calculateImportanceScore({
      ...event,
      outcomeMagnitude: event.outcomeMagnitude,
      humanFeedback: event.humanFeedback,
      affectedHumans: event.affectedHumans,
    } as ConsequenceMemoryEvent, daysOld);

    const fullEvent: ConsequenceMemoryEvent = {
      ...event,
      id: this.generateId(),
      importanceScore,
      ttlDays: this.calculateTTL(importanceScore),
    };

    this.memories.set(fullEvent.id, fullEvent);
    return fullEvent;
  }

  /**
   * Henter memory event
   */
  get(id: string): ConsequenceMemoryEvent | undefined {
    return this.memories.get(id);
  }

  /**
   * Henter alle memories
   */
  getAll(): ConsequenceMemoryEvent[] {
    return Array.from(this.memories.values());
  }

  /**
   * Henter memories sortert etter importance score
   */
  getSortedByImportance(): ConsequenceMemoryEvent[] {
    return this.getAll()
      .map(m => ({
        ...m,
        currentScore: this.calculateCurrentScore(m),
      }))
      .sort((a, b) => b.currentScore - a.currentScore);
  }

  /**
   * Henter relevante memories for en kontekst
   */
  getRelevantForContext(context: string, limit: number = 5): ConsequenceMemoryEvent[] {
    const contextWords = context.toLowerCase().split(/\s+/);
    
    return this.getAll()
      .map(m => {
        const eventWords = m.event.toLowerCase().split(/\s+/);
        const overlap = contextWords.filter(w => eventWords.includes(w)).length;
        const relevance = overlap / Math.max(contextWords.length, eventWords.length);
        
        return {
          memory: m,
          score: this.calculateCurrentScore(m) * (0.5 + 0.5 * relevance),
        };
      })
      .filter(item => item.score > this.config.pruneThreshold)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(item => item.memory);
  }

  /**
   * Oppdaterer eksisterende memory
   */
  update(id: string, updates: Partial<ConsequenceMemoryEvent>): boolean {
    const existing = this.memories.get(id);
    if (!existing) return false;

    const updated = { ...existing, ...updates };
    
    // Recalculate importance score
    const daysOld = this.getDaysOld(updated.occurredAt);
    updated.importanceScore = this.calculateImportanceScore(updated, daysOld);
    updated.ttlDays = this.calculateTTL(updated.importanceScore);

    this.memories.set(id, updated);
    return true;
  }

  /**
   * Sletter gammel/irrelevant memory
   */
  prune(): number {
    const toDelete: string[] = [];
    
    // Use Array.from to avoid downlevel iteration issues
    Array.from(this.memories.entries()).forEach(([id, event]) => {
      const currentScore = this.calculateCurrentScore(event);
      if (currentScore < this.config.pruneThreshold) {
        toDelete.push(id);
      }
    });

    for (const id of toDelete) {
      this.memories.delete(id);
    }

    return toDelete.length;
  }

  /**
   * Beregner nåværende score (med decay)
   */
  private calculateCurrentScore(event: ConsequenceMemoryEvent): number {
    const daysOld = this.getDaysOld(event.occurredAt);
    return this.calculateImportanceScore(event, daysOld);
  }

  /**
   * Beregner importance score med emosjonell og relasjonell vekting
   * 
   * Formula: (0.4 * factual + 0.4 * emotional + 0.2 * relational) * decay
   */
  private calculateImportanceScore(event: ConsequenceMemoryEvent, daysOld: number): number {
    const factualImpact = event.outcomeMagnitude; // 0-1
    
    const feedback = event.humanFeedback || {};
    const emotionalResonance = (
      (feedback.feltStress || 0) +
      (feedback.feltHope || 0) +
      (feedback.feltRegret || 0)
    ) / 3.0;
    
    const relationalRipple = event.affectedHumans * (feedback.empathyIndex || 0.5);
    
    // Mykere decay pga følelser varer lenger
    const decay = Math.exp(-this.config.decayRate * daysOld);
    
    return (0.4 * factualImpact + 0.4 * emotionalResonance + 0.2 * relationalRipple) * decay;
  }

  /**
   * Beregner TTL basert på importance score
   */
  private calculateTTL(importanceScore: number): number {
    // Høyere score = lengre TTL
    const factor = Math.max(0.1, importanceScore);
    return Math.round(this.config.defaultTTLDays * factor);
  }

  /**
   * Beregner antall dager siden hendelse
   */
  private getDaysOld(timestamp: string): number {
    const then = new Date(timestamp).getTime();
    const now = Date.now();
    return (now - then) / (1000 * 60 * 60 * 24);
  }

  /**
   * Genererer unik ID
   */
  private generateId(): string {
    return `memory_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Tømmer alle memories
   */
  clear(): void {
    this.memories.clear();
  }

  /**
   * Henter statistikk
   */
  getStats(): {
    total: number;
    averageScore: number;
    averageTTL: number;
  } {
    const all = this.getAll();
    if (all.length === 0) {
      return { total: 0, averageScore: 0, averageTTL: 0 };
    }

    const scores = all.map(m => this.calculateCurrentScore(m));
    const ttls = all.map(m => m.ttlDays);

    return {
      total: all.length,
      averageScore: scores.reduce((a, b) => a + b, 0) / scores.length,
      averageTTL: ttls.reduce((a, b) => a + b, 0) / ttls.length,
    };
  }
}

// Singleton instance
export const memoryStore = new MemoryStore();

/**
 * Memory Manager - Høy-nivå API
 */
export class MemoryManager {
  private store: MemoryStore;

  constructor(store: MemoryStore = memoryStore) {
    this.store = store;
  }

  /**
   * Lagrer hendelse fra challenge token
   */
  recordFromChallenge(
    token: SymbioticChallengeToken,
    outcome: string,
    affectedHumans: number = 1
  ): ConsequenceMemoryEvent {
    const humanFeedback: HumanFeedback = {
      // Estimer stress basert på challenge type
      feltStress: token.challengeType === "reject" ? 0.7 : 0.3,
      // Håp basert på at brukeren engasjerte seg
      feltHope: 0.5,
      empathyIndex: 0.6,
    };

    return this.store.save({
      event: `Challenge: ${token.challengeType} - ${token.humanChallenge.substring(0, 100)}`,
      outcome,
      outcomeMagnitude: token.weight,
      humanFeedback,
      affectedHumans,
      occurredAt: token.timestamp,
      relatedChallengeId: token.id,
    });
  }

  /**
   * Lagrer generisk hendelse
   */
  recordEvent(
    event: string,
    outcome: string,
    outcomeMagnitude: number,
    humanFeedback: HumanFeedback = {},
    affectedHumans: number = 1
  ): ConsequenceMemoryEvent {
    return this.store.save({
      event,
      outcome,
      outcomeMagnitude,
      humanFeedback,
      affectedHumans,
      occurredAt: new Date().toISOString(),
    });
  }

  /**
   * Henter relevant kontekst for RAG
   */
  getContextForQuery(query: string): string {
    const relevant = this.store.getRelevantForContext(query, 3);
    
    if (relevant.length === 0) {
      return "";
    }

    const contextLines = relevant.map(m => 
      `[${new Date(m.occurredAt).toLocaleDateString("no-NO")}] ${m.event} -> ${m.outcome}`
    );

    return "\nRelevant historisk kontekst:\n" + contextLines.join("\n");
  }

  /**
   * Kjører pruning av gamle memories
   */
  prune(): { deleted: number; remaining: number } {
    const before = this.store.getAll().length;
    const deleted = this.store.prune();
    const remaining = this.store.getAll().length;

    return { deleted, remaining };
  }

  /**
   * Henter statistikk
   */
  getStats(): ReturnType<MemoryStore["getStats"]> {
    return this.store.getStats();
  }
}

// Export singleton
export const memoryManager = new MemoryManager();

/**
 * Utility: Formatter memory for visning
 */
export function formatMemory(event: ConsequenceMemoryEvent): string {
  const date = new Date(event.occurredAt).toLocaleDateString("no-NO");
  const score = event.importanceScore.toFixed(2);
  const emoji = event.importanceScore > 0.5 ? "🔴" : event.importanceScore > 0.2 ? "🟡" : "🟢";
  
  return `${emoji} [${date}] (score: ${score}) ${event.event.substring(0, 80)}...`;
}
