/**
 * Symbiosis Decision API Route
 * 
 * POST /api/symbiosis/decision
 * - Genererer Symbiotic Decision Pillars fra input
 * - Wrapper rundt eksisterende sync/review-output
 * 
 * GET /api/symbiosis/decision
 * - Demo/test endpoint som returnerer sample pillars
 */

import { NextResponse } from "next/server";
import { decisionFormatter, handleDecisionRequest } from "@/lib/symbiosis";
import type { DecisionCreateRequest, SymbioticDecisionPillars } from "@roadmap/operator-contracts";

// Sample/demo pillars for testing
const samplePillars: SymbioticDecisionPillars = {
  reality: {
    facts: [
      "Domene: example.com",
      "Selskap: Example AS",
      "Sannhetssjekk: Verifisert",
      "Konfidens: 87%",
    ],
    sources: ["https://example.com/about"],
    verifiedAt: new Date().toISOString(),
  },
  interpretation: {
    operational: "Lead generert for Example AS i domene example.com.",
    whyThisMatters: "Potensiell salgsmulighet med høy konverteringssannsynlighet.",
  },
  uncertainty: {
    confidenceScore: 0.87,
    unknowns: ["Nøyaktig budsjett ikke verifisert"],
    dealbreakers: ["Ingen kjente dealbreakers"],
    requiresHumanIntuition: false,
  },
  stakes: {
    riskLevel: "low",
    description: "Verifisert lead med lav risiko. Standard oppfølging anbefales.",
  },
  choices: {
    choiceA: {
      label: "Godkjenn og send",
      action: "Fullfør godkjenning og send til kontakt",
      expectedOutcome: "Lead blir kontaktet via konfigurert kanal",
    },
    choiceB: {
      label: "Avvent verifikasjon",
      action: "Sett på vent til ytterligere verifikasjon er fullført",
      expectedOutcome: "Redusert risiko, men forsinket oppfølging",
    },
    choiceC: {
      label: "Avvis og logg",
      action: "Avvis leadet og logg årsak",
      expectedOutcome: "Ingen handling, men læring for fremtiden",
    },
  },
  recommendation: {
    recommendedChoice: "A",
    reasoning: "Lead er verifisert med høy konfidens (87%). Standard oppfølging anbefales.",
    supportedBy: "ai",
  },
  reversibility: {
    score: 0.7,
    rollbackTime: "Umiddelbar",
    rollbackCost: "Ingen",
    rollbackStrategy: "Kan angres via admin panel før sending",
  },
  coCreationScore: 3,
};

export async function GET(): Promise<NextResponse> {
  return NextResponse.json({
    success: true,
    message: "Symbiosis Decision API - Use POST to generate pillars from input",
    sample: samplePillars,
  });
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body: DecisionCreateRequest = await request.json();

    // Validate required fields
    if (!body.query) {
      return NextResponse.json(
        { error: "Missing required field: query" },
        { status: 400 }
      );
    }

    // Generate decision pillars
    const result = handleDecisionRequest(body);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      pillars: result.pillars,
      formatted: result.formattedOutput,
    });

  } catch (error) {
    console.error("Error generating decision:", error);
    return NextResponse.json(
      { error: "Failed to generate decision pillars" },
      { status: 500 }
    );
  }
}
