/**
 * Symbiosis Memory API Route
 * 
 * GET /api/symbiosis/memory
 * - Henter alle memory events
 * - Query params: ?context=<query> for relevante memories
 * 
 * POST /api/symbiosis/memory
 * - Lagrer ny hendelse i Memory of Consequence
 * 
 * DELETE /api/symbiosis/memory/prune
 * - Kjører pruning av gamle/irrelevante memories
 */

import { NextResponse } from "next/server";
import {
  memoryStore,
  memoryManager,
} from "@/lib/symbiosis";

export async function GET(request: Request): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(request.url);
    const context = searchParams.get("context");
    const limit = parseInt(searchParams.get("limit") || "10");

    let memories;
    let message: string;

    if (context) {
      // Hent relevante memories for kontekst
      memories = memoryStore.getRelevantForContext(context, limit);
      message = `Found ${memories.length} relevant memories for context`;
    } else {
      // Hent alle, sortert etter importance
      memories = memoryStore.getSortedByImportance().slice(0, limit);
      message = `Retrieved ${memories.length} memories (sorted by importance)`;
    }

    const stats = memoryStore.getStats();

    return NextResponse.json({
      success: true,
      message,
      stats,
      memories,
    });
  } catch (error) {
    console.error("Error fetching memories:", error);
    return NextResponse.json(
      { error: "Failed to fetch memories" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    const {
      event,
      outcome,
      outcomeMagnitude,
      humanFeedback,
      affectedHumans,
    } = body;

    if (!event || !outcome) {
      return NextResponse.json(
        { error: "Missing required fields: event, outcome" },
        { status: 400 }
      );
    }

    // Lagre hendelse
    const memoryEvent = memoryManager.recordEvent(
      event,
      outcome,
      outcomeMagnitude || 0.5,
      humanFeedback || {},
      affectedHumans || 1
    );

    return NextResponse.json({
      success: true,
      memory: memoryEvent,
      message: "Memory event recorded",
    }, { status: 201 });

  } catch (error) {
    console.error("Error recording memory:", error);
    return NextResponse.json(
      { error: "Failed to record memory" },
      { status: 500 }
    );
  }
}

export async function DELETE(request: Request): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get("action");

    if (action === "prune") {
      const result = memoryManager.prune();
      return NextResponse.json({
        success: true,
        message: `Pruned ${result.deleted} memories, ${result.remaining} remaining`,
        result,
      });
    }

    // Clear all (use with caution)
    if (action === "clear") {
      memoryStore.clear();
      return NextResponse.json({
        success: true,
        message: "All memories cleared",
      });
    }

    return NextResponse.json(
      { error: "Invalid action. Use ?action=prune or ?action=clear" },
      { status: 400 }
    );

  } catch (error) {
    console.error("Error pruning memories:", error);
    return NextResponse.json(
      { error: "Failed to prune memories" },
      { status: 500 }
    );
  }
}
