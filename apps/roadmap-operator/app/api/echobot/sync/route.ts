import { NextResponse } from 'next/server';
import { handleMissionSync } from '../../../../lib/echobot/bridge';
import type { EchobotLead } from '../../../../../packages/operator-contracts/src/echobot';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const lead = body.lead as EchobotLead;
    if (!lead) {
      return NextResponse.json({ error: 'Missing lead payload' }, { status: 400 });
    }
    const result = handleMissionSync(lead, {
      positive: body.positive,
      unsubscribe: body.unsubscribe,
      eventId: body.eventId,
    });
    return NextResponse.json({ status: 'created', result });
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
