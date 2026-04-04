import { NextResponse } from 'next/server';
import { handleStripeWebhook } from '../../../../../lib/echobot/bridge';

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const result = handleStripeWebhook(payload);
    if (result.status === 'created') {
      return NextResponse.json(result);
    }
    return NextResponse.json(result, { status: 202 });
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
