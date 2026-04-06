/**
 * Symbiosis Contradictions API Route
 * 
 * POST /api/symbiosis/contradictions
 * - Sjekker for konflikter mellom to kilder (NLI-basert)
 * - Triggere "Uncertainty Dance" ved høy score
 * 
 * GET /api/symbiosis/contradictions
 * - Henter alle registrerte contradictions
 * 
 * PATCH /api/symbiosis/contradictions
 * - Lagrer menneskelig resolusjon av contradiction
 */

import { NextResponse } from "next/server";
import { contradictionDetector, contradictionStore } from "@/lib/symbiosis";
import type { ContradictionCheckRequest } from "@roadmap/operator-contracts";

export async function GET(): Promise<NextResponse> {
  try {
    const contradictions = contradictionStore.getAll();
    const unresolved = contradictionStore.getUnresolved();
    
    return NextResponse.json({
      success: true,
      count: contradictions.length,
      unresolvedCount: unresolved.length,
      contradictions,
    });
  } catch (error) {
    console.error("Error fetching contradictions:", error);
    return NextResponse.json(
      { error: "Failed to fetch contradictions" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body: ContradictionCheckRequest = await request.json();

    // Validate required fields
    if (!body.sourceA || !body.sourceB) {
      return NextResponse.json(
        { error: "Missing required fields: sourceA, sourceB" },
        { status: 400 }
      );
    }

    // Check for contradiction
    const result = await contradictionDetector.handleCheckRequest(body);

    // If contradiction found, trigger uncertainty dance
    let uncertaintyDance = null;
    if (result.contradiction) {
      uncertaintyDance = contradictionDetector.triggerUncertaintyDance(result.contradiction);
    }

    return NextResponse.json({
      success: true,
      hasContradiction: result.hasContradiction,
      score: result.score,
      contradiction: result.contradiction,
      uncertaintyDance,
    });

  } catch (error) {
    console.error("Error checking contradiction:", error);
    return NextResponse.json(
      { error: "Failed to check contradiction" },
      { status: 500 }
    );
  }
}

export async function PATCH(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    const { pairId, preferredSource, reasoning } = body;

    if (!pairId || !preferredSource) {
      return NextResponse.json(
        { error: "Missing required fields: pairId, preferredSource" },
        { status: 400 }
      );
    }

    const updated = contradictionDetector.resolveContradiction(pairId, {
      preferredSource,
      reasoning: reasoning || "Ingen begrunnelse gitt",
    });

    if (!updated) {
      return NextResponse.json(
        { error: "Contradiction not found" },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      contradiction: updated,
      message: "Contradiction resolved with human intuition",
    });

  } catch (error) {
    console.error("Error resolving contradiction:", error);
    return NextResponse.json(
      { error: "Failed to resolve contradiction" },
      { status: 500 }
    );
  }
}
