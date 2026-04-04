import { NextResponse } from 'next/server';
import { loadStats } from '../../../../lib/echobot/bridge';

export async function GET() {
  try {
    const stats = loadStats();
    return NextResponse.json(stats);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
