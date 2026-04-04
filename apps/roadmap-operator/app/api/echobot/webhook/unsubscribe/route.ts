import { NextResponse } from "next/server";

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    
    const { email, leadId, reason } = body;
    
    if (!email && !leadId) {
      return NextResponse.json(
        { error: "Missing email or leadId" },
        { status: 400 }
      );
    }

    // TODO:
    // 1. Find lead by email or leadId
    // 2. Mark as optedOut = true
    // 3. Log reason if provided
    console.log("Unsubscribe request:", { email, leadId, reason });

    return NextResponse.json({ success: true, optedOut: true });
  } catch (error) {
    console.error("Error processing unsubscribe:", error);
    return NextResponse.json(
      { error: "Failed to process unsubscribe" },
      { status: 500 }
    );
  }
}
