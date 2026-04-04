import { NextResponse } from "next/server";
import type { EchobotLead, RoadmapSyncPreview, RoadmapSyncResult } from "@roadmap/operator-contracts";

// Mock data store (replace with actual DB)
const leadsStore: Map<string, EchobotLead> = new Map();

export async function GET(request: Request): Promise<NextResponse> {
  try {
    const { searchParams } = new URL(request.url);
    const leadId = searchParams.get("leadId");
    const preview = searchParams.get("preview") === "true";

    if (!leadId) {
      return NextResponse.json(
        { error: "Missing leadId parameter" },
        { status: 400 }
      );
    }

    const lead = leadsStore.get(leadId);
    if (!lead) {
      return NextResponse.json({ error: "Lead not found" }, { status: 404 });
    }

    if (preview) {
      // Return preview of what would be synced
      const preview: RoadmapSyncPreview = {
        lead,
        payload: {
          missionTitle: `Echobot: ${lead.companyName}`,
          origin: "echobot",
          proofDefinition: {
            description: lead.hypothesis,
          },
          nextActions: [
            "Send personalized outreach",
            "Schedule discovery call",
            "Capture proof of value",
          ],
        },
      };
      return NextResponse.json(preview);
    }

    return NextResponse.json({ lead });
  } catch (error) {
    console.error("Error fetching sync data:", error);
    return NextResponse.json(
      { error: "Failed to fetch sync data" },
      { status: 500 }
    );
  }
}

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    const { leadId, operatorNotes } = body;

    if (!leadId) {
      return NextResponse.json(
        { error: "Missing leadId" },
        { status: 400 }
      );
    }

    const lead = leadsStore.get(leadId);
    if (!lead) {
      return NextResponse.json({ error: "Lead not found" }, { status: 404 });
    }

    // Fail-closed: Check for positive signal
    if (lead.replySentiment !== "positive" && !lead.stripeInvoiceUrl) {
      return NextResponse.json(
        { error: "Sync requires positive reply or payment" },
        { status: 403 }
      );
    }

    // Fail-closed: Check opted out
    if (lead.optedOut) {
      return NextResponse.json(
        { error: "Lead has opted out" },
        { status: 403 }
      );
    }

    // TODO: Actually create mission in Roadmap
    const result: RoadmapSyncResult = {
      missionId: `mission-${Date.now()}`,
      createdAt: new Date().toISOString(),
      status: "created",
    };

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error syncing to mission:", error);
    return NextResponse.json(
      { error: "Failed to sync to mission" },
      { status: 500 }
    );
  }
}
