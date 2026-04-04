import { NextResponse } from "next/server";

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    
    // Validate webhook payload
    const { leadId, sentiment, replyText } = body;
    if (!leadId || !sentiment) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    // TODO: Update lead in database with reply sentiment
    console.log("Reply webhook received:", { leadId, sentiment, replyText });

    return NextResponse.json({ success: true, processed: true });
  } catch (error) {
    console.error("Error processing reply webhook:", error);
    return NextResponse.json(
      { error: "Failed to process webhook" },
      { status: 500 }
    );
  }
}
