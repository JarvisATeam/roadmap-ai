import { NextResponse } from 'next/server';
import { loadReviewQueue } from '../../../../lib/echobot/bridge';

export async function GET() {
  try {
    const queue = loadReviewQueue();
    return NextResponse.json(queue);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
