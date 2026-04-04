import { NextResponse } from 'next/server';
import { buildSyncPreview } from '../../../../lib/echobot/bridge';
import type { EchobotLead } from '../../../../../packages/operator-contracts/src/echobot';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const lead = body.lead as EchobotLead;
    if (!lead) {
      return NextResponse.json({ error: 'Missing lead payload' }, { status: 400 });
    }
    const preview = buildSyncPreview(lead);
    return NextResponse.json(preview);
  } catch (error) {
    return NextResponse.json({ error: (error as Error).message }, { status: 500 });
  }
}
