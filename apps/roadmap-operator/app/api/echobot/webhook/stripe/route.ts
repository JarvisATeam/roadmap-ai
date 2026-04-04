import { NextResponse } from "next/server";

// Deduplication store (replace with Redis/DB in production)
const processedEvents = new Set<string>();

export async function POST(request: Request): Promise<NextResponse> {
  try {
    const body = await request.json();
    
    // Extract Stripe event details
    const { id: eventId, type: eventType, data } = body;
    
    if (!eventId || !eventType) {
      return NextResponse.json(
        { error: "Invalid webhook payload" },
        { status: 400 }
      );
    }

    // Deduplication check
    if (processedEvents.has(eventId)) {
      return NextResponse.json({ success: true, duplicate: true });
    }

    // Only process invoice.paid events
    if (eventType !== "invoice.paid") {
      return NextResponse.json({ success: true, ignored: true });
    }

    const { customer_email, hosted_invoice_url } = data?.object || {};
    
    // TODO: 
    // 1. Find lead by email
    // 2. Update lead with stripeInvoiceUrl
    // 3. Trigger n8n onboarding workflow
    console.log("Stripe payment received:", { 
      eventId, 
      customer_email, 
      hosted_invoice_url 
    });

    // Mark event as processed
    processedEvents.add(eventId);

    return NextResponse.json({ success: true, processed: true });
  } catch (error) {
    console.error("Error processing Stripe webhook:", error);
    return NextResponse.json(
      { error: "Failed to process webhook" },
      { status: 500 }
    );
  }
}
