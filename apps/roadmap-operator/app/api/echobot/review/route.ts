import { NextResponse } from "next/server";
import type { EchobotLead } from "@roadmap/operator-contracts";

// In-memory store for development (replace with DB)
let reviewQueue: EchobotLead[] = [];

export async function GET(): Promise<NextResponse> {
  try {
    // TODO: Fetch from actual data source
    // Return leads that need review (QUEUE or PENDING status)
    const queue = reviewQueue.filter(
      (lead) => lead.sendStatus === "QUEUE" || lead.truthStatus === "PENDING"
    );

    return NextResponse.json(queue);
  } catch (error) {
    console.error("Error fetching review queue:", error);
    return NextResponse.json(
      { error: "Failed to fetch review queue" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    const { leadId, action, notes } = body;

    if (!leadId || !action) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // Find lead in queue
    const leadIndex = reviewQueue.findIndex((l) => l.id === leadId);
    if (leadIndex === -1) {
      return NextResponse.json({ error: "Lead not found" }, { status: 404 });
    }

    // Update lead based on action
    if (action === "approve") {
      reviewQueue[leadIndex] = {
        ...reviewQueue[leadIndex],
        sendStatus: "APPROVED",
      };
    } else if (action === "reject") {
      reviewQueue[leadIndex] = {
        ...reviewQueue[leadIndex],
        sendStatus: "REJECTED",
      };
    } else {
      return NextResponse.json({ error: "Invalid action" }, { status: 400 });
    }

    return NextResponse.json({ success: true, leadId, action, notes });
  } catch (error) {
    console.error("Error processing review:", error);
    return NextResponse.json(
      { error: "Failed to process review" },
      { status: 500 }
    );
  }
}
