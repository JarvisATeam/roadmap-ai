/**
 * Symbiosis Decision Module
 * 
 * Wrapper rundt eksisterende sync/review-output som formaterer
 * alle svar inn i Symbiotic Decision Pillars kontrakten.
 */

import {
  SymbioticDecisionPillars,
  RealityPillar,
  InterpretationPillar,
  UncertaintyPillar,
  StakesPillar,
  ChoicesPillar,
  ChoiceOption,
  RecommendationPillar,
  ReversibilityPillar,
  RiskLevel,
  DecisionCreateRequest,
  DecisionCreateResponse,
  EchobotLead,
  EchobotReviewResult,
} from "@roadmap/operator-contracts";

/**
 * Input for decision-pillar generering
 */
export interface DecisionInput {
  /** Opprinnelig query eller kontekst */
  query: string;
  
  /** Eksisterende ECHOBOT lead data */
  echobotLead?: EchobotLead;
  
  /** Review resultat fra eksisterende system */
  reviewResult?: EchobotReviewResult;
  
  /** Ekstern datakontekst */
  sourceData?: Record<string, unknown>;
  
  /** Menneskelig input hvis tilgjengelig */
  humanInput?: string;
  
  /** Konfidens-score fra eksisterende system */
  confidenceScore?: number;
}

/**
 * Decision Formatter - Hovedklasse for å bygge Decision Pillars
 */
export class DecisionFormatter {
  /**
   * Hovedmetode: Konverterer eksisterende output til Symbiotic Decision Pillars
   */
  formatToPillars(input: DecisionInput): SymbioticDecisionPillars {
    return {
      reality: this.buildRealityPillar(input),
      interpretation: this.buildInterpretationPillar(input),
      uncertainty: this.buildUncertaintyPillar(input),
      stakes: this.buildStakesPillar(input),
      choices: this.buildChoicesPillar(input),
      recommendation: this.buildRecommendationPillar(input),
      reversibility: this.buildReversibilityPillar(input),
      coCreationScore: this.calculateCoCreationScore(input),
    };
  }

  /**
   * Bygger Reality Pillar fra eksisterende data
   */
  private buildRealityPillar(input: DecisionInput): RealityPillar {
    const facts: string[] = [];
    const sources: string[] = [];

    // Trekk fakta fra ECHOBOT lead
    if (input.echobotLead) {
      facts.push(`Domene: ${input.echobotLead.domain}`);
      facts.push(`Selskap: ${input.echobotLead.companyName}`);
      facts.push(`Kontakt: ${input.echobotLead.contactEmail}`);
      
      if (input.echobotLead.truthStatus === "PASSED") {
        facts.push("Sannhetssjekk: Verifisert");
      }
      
      if (input.echobotLead.evidenceUrl) {
        sources.push(input.echobotLead.evidenceUrl);
      }
    }

    // Trekk fakta fra review result
    if (input.reviewResult?.truth) {
      facts.push(`Konfidens: ${(input.reviewResult.truth.confidenceScore * 100).toFixed(0)}%`);
      if (input.reviewResult.truth.evidenceSummary) {
        facts.push(input.reviewResult.truth.evidenceSummary);
      }
      if (input.reviewResult.truth.evidenceUrl) {
        sources.push(input.reviewResult.truth.evidenceUrl);
      }
    }

    return {
      facts: facts.length > 0 ? facts : ["Ingen spesifikke fakta tilgjengelig"],
      sources: sources.length > 0 ? sources : undefined,
      verifiedAt: new Date().toISOString(),
    };
  }

  /**
   * Bygger Interpretation Pillar
   */
  private buildInterpretationPillar(input: DecisionInput): InterpretationPillar {
    let operational = "Ingen spesifikk operativ betydning identifisert.";
    let whyThisMatters = "Kontekst ikke tilgjengelig.";

    if (input.echobotLead) {
      operational = `Lead generert for ${input.echobotLead.companyName} i domene ${input.echobotLead.domain}.`;
      whyThisMatters = "Potensiell salgsmulighet krever oppfølging.";
      
      if (input.echobotLead.hypothesis) {
        whyThisMatters = input.echobotLead.hypothesis;
      }
    }

    return {
      operational,
      whyThisMatters,
    };
  }

  /**
   * Bygger Uncertainty Pillar
   */
  private buildUncertaintyPillar(input: DecisionInput): UncertaintyPillar {
    const unknowns: string[] = [];
    const dealbreakers: string[] = [];
    
    let confidenceScore = input.confidenceScore || 0.5;

    if (input.echobotLead) {
      if (input.echobotLead.truthStatus === "PENDING") {
        unknowns.push("Sannhetssjekk ikke fullført");
        confidenceScore *= 0.8;
      }
      
      if (!input.echobotLead.contactName) {
        unknowns.push("Navn på kontaktperson ikke verifisert");
      }
      
      if (input.echobotLead.truthStatus === "FAILED") {
        dealbreakers.push("Sannhetssjekk feilet - data kan være unøyaktige");
        confidenceScore *= 0.3;
      }
    }

    if (input.reviewResult && !input.reviewResult.approved) {
      dealbreakers.push("Review avviste forslaget");
      confidenceScore *= 0.2;
    }

    return {
      confidenceScore: Math.max(0, Math.min(1, confidenceScore)),
      unknowns: unknowns.length > 0 ? unknowns : ["Ingen spesifikke usikkerheter identifisert"],
      dealbreakers: dealbreakers.length > 0 ? dealbreakers : ["Ingen kjente dealbreakers"],
      requiresHumanIntuition: confidenceScore < 0.7 || dealbreakers.length > 0,
    };
  }

  /**
   * Bygger Stakes Pillar
   */
  private buildStakesPillar(input: DecisionInput): StakesPillar {
    let riskLevel: RiskLevel = "low";
    let description = "Lav risiko ved denne handlingen.";
    let quantifiedRisk: string | undefined;

    if (input.echobotLead) {
      // Vurder risiko basert på truth status
      switch (input.echobotLead.truthStatus) {
        case "FAILED":
          riskLevel = "high";
          description = "Høy risiko - sannhetssjekk feilet. Kan skade omdømme ved kontakt.";
          quantifiedRisk = "Potensiell omdømmeskade";
          break;
        case "PENDING":
          riskLevel = "medium";
          description = "Moderat risiko - avventer verifikasjon.";
          break;
        case "PASSED":
          riskLevel = "low";
          description = "Verifisert lead med lav risiko.";
          break;
      }

      // Juster basert på send status
      if (input.echobotLead.sendStatus === "REJECTED") {
        riskLevel = "high";
        description = "Tidligere avvist - krever ny vurdering.";
      }
    }

    return {
      riskLevel,
      description,
      quantifiedRisk,
    };
  }

  /**
   * Bygger Choices Pillar
   */
  private buildChoicesPillar(input: DecisionInput): ChoicesPillar {
    const choiceA: ChoiceOption = {
      label: "Godkjenn og send",
      action: "Fullfør godkjenning og send til kontakt",
      expectedOutcome: "Lead blir kontaktet via konfigurert kanal",
    };

    const choiceB: ChoiceOption = {
      label: "Avvent verifikasjon",
      action: "Sett på vent til ytterligere verifikasjon er fullført",
      expectedOutcome: "Redusert risiko, men forsinket oppfølging",
    };

    const choiceC: ChoiceOption = {
      label: "Avvis og logg",
      action: "Avvis leadet og logg årsak",
      expectedOutcome: "Ingen handling, men læring for fremtiden",
    };

    return {
      choiceA,
      choiceB,
      choiceC,
    };
  }

  /**
   * Bygger Recommendation Pillar
   */
  private buildRecommendationPillar(input: DecisionInput): RecommendationPillar {
    let recommendedChoice: "A" | "B" | "C" = "B";
    let reasoning = "Standard anbefaling er å avvente full verifikasjon.";
    let supportedBy: "ai" | "human" | "co-created" = "ai";

    if (input.echobotLead) {
      if (input.echobotLead.truthStatus === "PASSED" && 
          input.echobotLead.sendStatus === "APPROVED") {
        recommendedChoice = "A";
        reasoning = "Lead er verifisert og godkjent for sending.";
      } else if (input.echobotLead.truthStatus === "FAILED" ||
                 input.echobotLead.sendStatus === "REJECTED") {
        recommendedChoice = "C";
        reasoning = "For mange røde flagg - anbefaler avvisning.";
      }
    }

    if (input.reviewResult?.approved) {
      recommendedChoice = "A";
      reasoning = input.reviewResult.reviewerNotes || "Godkjent av reviewer.";
      supportedBy = "human";
    }

    if (input.humanInput) {
      supportedBy = "co-created";
      reasoning += ` (inkluderer menneskelig input: ${input.humanInput})`;
    }

    return {
      recommendedChoice,
      reasoning,
      supportedBy,
    };
  }

  /**
   * Bygger Reversibility Pillar
   */
  private buildReversibilityPillar(input: DecisionInput): ReversibilityPillar {
    let score = 0.7; // De fleste operasjoner er ganske reversible
    let rollbackTime = "Umiddelbar";
    let rollbackCost = "Ingen";
    let rollbackStrategy = "Kan angres via admin panel";

    if (input.echobotLead?.sendStatus === "SENT") {
      score = 0.1;
      rollbackTime = "24-48 timer";
      rollbackCost = "Omdømmerisiko";
      rollbackStrategy = "Send oppfølgingsmelding med korreksjon";
    }

    return {
      score,
      rollbackTime,
      rollbackCost,
      rollbackStrategy,
    };
  }

  /**
   * Beregner Co-Creation Score (0-10)
   */
  private calculateCoCreationScore(input: DecisionInput): number {
    let score = 3; // Baseline: ren AI-generering

    // Øk score hvis menneskelig input finnes
    if (input.humanInput) {
      score += 3;
    }

    // Øk score hvis review er gjort
    if (input.reviewResult) {
      score += 2;
    }

    // Øk score hvis reviewer notes finnes
    if (input.reviewResult?.reviewerNotes) {
      score += 2;
    }

    return Math.min(10, score);
  }

  /**
   * Formatterer pillars til leservennlig output
   */
  formatToString(pillars: SymbioticDecisionPillars): string {
    const lines: string[] = [];
    
    lines.push("=== SYMBIOTISK BESLUTNINGSSTØTTE ===\n");
    
    lines.push("📋 REALITY (Fakta):");
    pillars.reality.facts.forEach(f => lines.push(`  • ${f}`));
    
    lines.push("\n💡 INTERPRETATION (Betydning):");
    lines.push(`  Operativ: ${pillars.interpretation.operational}`);
    lines.push(`  Hvorfor: ${pillars.interpretation.whyThisMatters}`);
    
    lines.push("\n❓ UNCERTAINTY (Usikkerhet):");
    lines.push(`  Konfidens: ${(pillars.uncertainty.confidenceScore * 100).toFixed(0)}%`);
    lines.push(`  Krever intuisjon: ${pillars.uncertainty.requiresHumanIntuition ? "Ja" : "Nei"}`);
    
    lines.push("\n⚠️ STAKES (Risiko):");
    lines.push(`  Nivå: ${pillars.stakes.riskLevel.toUpperCase()}`);
    lines.push(`  ${pillars.stakes.description}`);
    
    lines.push("\n🎯 CHOICES (Valg):");
    lines.push(`  A: ${pillars.choices.choiceA.label} - ${pillars.choices.choiceA.action}`);
    lines.push(`  B: ${pillars.choices.choiceB.label} - ${pillars.choices.choiceB.action}`);
    lines.push(`  C: ${pillars.choices.choiceC.label} - ${pillars.choices.choiceC.action}`);
    
    lines.push("\n✅ RECOMMENDATION:");
    lines.push(`  Valg ${pillars.recommendation.recommendedChoice}: ${pillars.recommendation.reasoning}`);
    lines.push(`  Støttet av: ${pillars.recommendation.supportedBy}`);
    
    lines.push("\n🔄 REVERSIBILITY (Angrepunkt):");
    lines.push(`  Score: ${(pillars.reversibility.score * 100).toFixed(0)}%`);
    if (pillars.reversibility.rollbackStrategy) {
      lines.push(`  Strategi: ${pillars.reversibility.rollbackStrategy}`);
    }
    
    lines.push("\n🤝 CO-CREATION SCORE:");
    lines.push(`  ${pillars.coCreationScore}/10`);
    
    return lines.join("\n");
  }
}

// Export singleton
export const decisionFormatter = new DecisionFormatter();

/**
 * Handler for decision requests
 */
export function handleDecisionRequest(request: DecisionCreateRequest): DecisionCreateResponse {
  // Validate required fields
  if (!request.query?.trim()) {
    return {
      success: false,
      error: "Missing required field: query",
    };
  }

  try {
    const input: DecisionInput = {
      query: request.query,
      sourceData: request.sourceData,
      humanInput: request.humanInput,
    };

    const pillars = decisionFormatter.formatToPillars(input);
    const formattedOutput = decisionFormatter.formatToString(pillars);

    return {
      success: true,
      pillars,
      formattedOutput,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : "Unknown error",
    };
  }
}

/**
 * Integrasjon med eksisterende ECHOBOT review result
 */
export function formatEchobotReviewToPillars(
  reviewResult: EchobotReviewResult,
  humanInput?: string
): SymbioticDecisionPillars {
  const input: DecisionInput = {
    query: `Review of lead: ${reviewResult.lead.companyName}`,
    echobotLead: reviewResult.lead,
    reviewResult,
    humanInput,
  };

  return decisionFormatter.formatToPillars(input);
}
