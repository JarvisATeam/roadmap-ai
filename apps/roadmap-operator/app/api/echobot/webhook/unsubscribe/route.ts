import { NextResponse } from 'next/server';
import { handleUnsubscribeWebhook } from '../../../../../lib/echobot/bridge';

export async function POST(request: Request) {
  try {
    const payload = await request.json();
    const result = handleUnsubscribeWebhook(payload);
    if (result.status === 'blocked') {
      return NextResponse.json(result);
    }
    return NextResponse.json(result, { status: 202 });
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
