/**
 * Symbiosis Contradiction Module
 * 
 * Oppdager og eksponerer konflikter i datagrunnlag via NLI-basert filter.
 * Triggere "uncertainty dance" når sterke kontradiksjoner oppdages.
 */

import {
  ContradictionPair,
  ContradictionStatus,
  HumanResolution,
  HumanIntuitionVector,
  ContradictionCheckRequest,
  ContradictionCheckResponse,
} from "@roadmap/operator-contracts";

/**
 * Konfigurasjon for contradiction detection
 */
export interface ContradictionConfig {
  /** Terskel for å trigge contradiction (0-1) */
  threshold: number;
  
  /** Minimum score for å lagre contradiction */
  minScore: number;
  
  /** Auto-trigger uncertainty dance ved høy score */
  autoTriggerDance: boolean;
  
  /** Terskel for auto-trigger */
  autoTriggerThreshold: number;
}

const DEFAULT_CONFIG: ContradictionConfig = {
  threshold: 0.7,
  minScore: 0.5,
  autoTriggerDance: false, // Manuel i S1
  autoTriggerThreshold: 0.85,
};

/**
 * NLI Resultat (simulert - vil integrere med faktisk DeBERTa i P2)
 */
interface NLIResult {
  label: "CONTRADICTION" | "ENTAILMENT" | "NEUTRAL";
  score: number;
}

/**
 * Contradiction Store
 */
class ContradictionStore {
  private contradictions: Map<string, ContradictionPair> = new Map();

  save(pair: ContradictionPair): void {
    this.contradictions.set(pair.id, pair);
  }

  get(id: string): ContradictionPair | undefined {
    return this.contradictions.get(id);
  }

  getAll(): ContradictionPair[] {
    return Array.from(this.contradictions.values());
  }

  getUnresolved(): ContradictionPair[] {
    return this.getAll().filter(c => c.status === "unresolved");
  }

  update(id: string, updates: Partial<ContradictionPair>): boolean {
    const existing = this.contradictions.get(id);
    if (!existing) return false;
    this.contradictions.set(id, { ...existing, ...updates });
    return true;
  }

  clear(): void {
    this.contradictions.clear();
  }
}

export const contradictionStore = new ContradictionStore();

/**
 * Contradiction Detector
 */
export class ContradictionDetector {
  private config: ContradictionConfig;

  constructor(config: Partial<ContradictionConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * Sjekker for contradiction mellom to kilder
   * 
   * NOTE: I S1 bruker vi simulert NLI. I P2 integreres faktisk
   * DeBERTa NLI-modell (cross-encoder/nli-deberta-v3-large)
   */
  async checkContradiction(
    sourceA: string,
    sourceB: string
  ): Promise<ContradictionCheckResponse> {
    // Simulert NLI (erstattes med faktisk modell i P2)
    const nliResult = await this.simulateNLI(sourceA, sourceB);

    if (nliResult.label === "CONTRADICTION" && nliResult.score > this.config.threshold) {
      const pair: ContradictionPair = {
        id: this.generateId(),
        sourceA,
        sourceB,
        contradictionScore: nliResult.score,
        detectedAt: new Date().toISOString(),
        status: "unresolved",
      };

      contradictionStore.save(pair);

      return {
        hasContradiction: true,
        score: nliResult.score,
        contradiction: pair,
      };
    }

    return {
      hasContradiction: false,
      score: nliResult.score,
    };
  }

  /**
   * Håndterer contradiction request fra API
   */
  async handleCheckRequest(request: ContradictionCheckRequest): Promise<ContradictionCheckResponse> {
    return this.checkContradiction(request.sourceA, request.sourceB);
  }

  /**
   * Simulert NLI (placeholder for DeBERTa)
   * 
   * I P2 erstattes dette med:
   * ```python
   * from transformers import pipeline
   * nli = pipeline("text-classification", model="cross-encoder/nli-deberta-v3-large")
   * result = nli(f"{sourceA} {source_B}")
   * ```
   */
  private async simulateNLI(sourceA: string, sourceB: string): Promise<NLIResult> {
    // Enkel heuristik for S1:
    // Sjekk for motsetningsindikatorer
    const contradictionIndicators = [
      ["økt", "redusert"],
      ["positiv", "negativ"],
      ["suksess", "feil"],
      ["støtter", "motsetter"],
      ["ja", "nei"],
      ["alltid", "aldri"],
    ];

    const aLower = sourceA.toLowerCase();
    const bLower = sourceB.toLowerCase();

    // Sjekk for direkte motsetninger
    for (const [pos, neg] of contradictionIndicators) {
      const aHasPos = aLower.includes(pos);
      const aHasNeg = aLower.includes(neg);
      const bHasPos = bLower.includes(pos);
      const bHasNeg = bLower.includes(neg);

      if ((aHasPos && bHasNeg) || (aHasNeg && bHasPos)) {
        return {
          label: "CONTRADICTION",
          score: 0.75 + Math.random() * 0.15, // 0.75-0.90
        };
      }
    }

    // Sjekk for semantisk motsetning (enkel string similarity)
    const similarity = this.calculateSimilarity(sourceA, sourceB);
    if (similarity < 0.3) {
      // Veldig ulike utsagn kan indikere kontekstuell forskjell
      return {
        label: "NEUTRAL",
        score: 0.4 + Math.random() * 0.2,
      };
    }

    return {
      label: "NEUTRAL",
      score: 0.3 + Math.random() * 0.3,
    };
  }

  /**
   * Enkel string similarity (Jaccard)
   */
  private calculateSimilarity(a: string, b: string): number {
    const aWords = a.toLowerCase().split(/\s+/);
    const bWords = b.toLowerCase().split(/\s+/);
    
    const aSet = new Set(aWords);
    const bSet = new Set(bWords);
    
    // Calculate intersection using Array.from for compatibility
    let intersection = 0;
    Array.from(aSet).forEach(word => {
      if (bSet.has(word)) {
        intersection++;
      }
    });
    
    // Calculate union
    const union = new Set(aWords.concat(bWords));
    
    return intersection / union.size;
  }

  /**
   * Triggere "Uncertainty Dance"
   * Spør mennesket om å velge mellom motstridende kilder
   */
  triggerUncertaintyDance(pair: ContradictionPair): {
    question: string;
    pair: ContradictionPair;
  } {
    return {
      question: `Konflikt oppdaget mellom to kilder:

KILDE A: "${pair.sourceA}"

KILDE B: "${pair.sourceB}"

Hvilken kilde føles mest riktig for deg, og hvorfor?`,
      pair,
    };
  }

  /**
   * Lagrer menneskelig resolusjon av contradiction
   */
  resolveContradiction(
    pairId: string,
    resolution: Omit<HumanResolution, "resolvedAt">
  ): ContradictionPair | null {
    const pair = contradictionStore.get(pairId);
    if (!pair) return null;

    const humanResolution: HumanResolution = {
      ...resolution,
      resolvedAt: new Date().toISOString(),
    };

    // Opprett intuition vector hvis resolution inneholder begrunnelse
    if (resolution.reasoning) {
      humanResolution.intuitionVector = this.createIntuitionVector(
        pair,
        resolution.reasoning,
        resolution.preferredSource
      );
    }

    const statusMap: Record<string, ContradictionStatus> = {
      A: "resolved_a",
      B: "resolved_b",
      both: "both_valid",
      neither: "irrelevant",
    };

    const updated: ContradictionPair = {
      ...pair,
      status: statusMap[resolution.preferredSource] || "unresolved",
      humanResolution,
    };

    contradictionStore.save(updated);
    return updated;
  }

  /**
   * Oppretter Human Intuition Vector fra resolution
   */
  private createIntuitionVector(
    pair: ContradictionPair,
    reasoning: string,
    preferredSource: "A" | "B" | "both" | "neither"
  ): HumanIntuitionVector {
    return {
      id: `intuition_${pair.id}`,
      intuition: reasoning,
      context: `Contradiction resolution: preferred ${preferredSource}`,
      weight: pair.contradictionScore,
      tags: ["contradiction", "resolution", preferredSource.toLowerCase()],
      createdAt: new Date().toISOString(),
      sourceContradictionId: pair.id,
    };
  }

  /**
   * Henter alle uløste contradictions
   */
  getUnresolvedContradictions(): ContradictionPair[] {
    return contradictionStore.getUnresolved();
  }

  /**
   * Genererer unik ID
   */
  private generateId(): string {
    return `contradiction_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// Export singleton
export const contradictionDetector = new ContradictionDetector();

/**
 * Batch-sjekk av flere kilder
 */
export async function checkMultipleSources(
  sources: string[]
): Promise<ContradictionPair[]> {
  const contradictions: ContradictionPair[] = [];

  for (let i = 0; i < sources.length; i++) {
    for (let j = i + 1; j < sources.length; j++) {
      const result = await contradictionDetector.checkContradiction(
        sources[i],
        sources[j]
      );
      if (result.contradiction) {
        contradictions.push(result.contradiction);
      }
    }
  }

  return contradictions;
}

/**
 * Formatter contradiction for visning
 */
export function formatContradiction(pair: ContradictionPair): string {
  const statusEmoji: Record<ContradictionStatus, string> = {
    unresolved: "⚠️",
    resolved_a: "✅ A",
    resolved_b: "✅ B",
    both_valid: "✅ Both",
    irrelevant: "🚫",
  };

  return `${statusEmoji[pair.status]} Konflikt (${(pair.contradictionScore * 100).toFixed(0)}%): "${pair.sourceA.substring(0, 50)}..." vs "${pair.sourceB.substring(0, 50)}..."`;
}
