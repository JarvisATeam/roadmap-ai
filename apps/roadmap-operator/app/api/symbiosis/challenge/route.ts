/**
 * Symbiosis Challenge API Route
 * 
 * POST /api/symbiosis/challenge
 * - Aksepterer menneskelig korrigering av AI-output
 * - Logger som co-creation token for RLAIF
 * 
 * GET /api/symbiosis/challenge
 * - Henter alle challenges (for analyse/dashboard)
 */

import { NextResponse } from "next/server";
import { challengeManager, challengeStore } from "@/lib/symbiosis";
import type { ChallengeCreateRequest } from "@roadmap/operator-contracts";

export async function GET(): Promise<NextResponse> {
  try {
    const challenges = challengeStore.getAll();
    return NextResponse.json({
      success: true,
      count: challenges.length,
      challenges,
    });
  } catch (error) {
    console.error("Error fetching challenges:", error);
    return NextResponse.json(
      { error: "Failed to fetch challenges" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body: ChallengeCreateRequest = await request.json();

    // Validate required fields
    if (!body.originalOutput || !body.humanChallenge) {
      return NextResponse.json(
        { error: "Missing required fields: originalOutput, humanChallenge" },
        { status: 400 }
      );
    }

    // Process challenge
    const result = challengeManager.handleChallengeRequest(body);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      token: result.token,
      message: "Challenge logged as co-creation token",
    }, { status: 201 });

  } catch (error) {
    console.error("Error processing challenge:", error);
    return NextResponse.json(
      { error: "Failed to process challenge" },
      { status: 500 }
    );
  }
}
