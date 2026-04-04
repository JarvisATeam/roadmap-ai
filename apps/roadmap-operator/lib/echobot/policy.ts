import type { EchobotLead } from '../../../../packages/operator-contracts/src/echobot';
import type { ProofDefinition, RoadmapMissionPayload } from '../../../../packages/operator-contracts/src/roadmap-sync';

type ReplyPayload = { sentiment?: string; eventType?: string };
type StripePayload = { type?: string; data?: { object?: { id?: string; status?: string } } };
type UnsubscribePayload = { email?: string; reason?: string };

export function isPositiveReplySignal(payload: ReplyPayload): boolean {
  const sentiment = payload.sentiment?.toLowerCase();
  return payload.eventType === 'reply_positive' || sentiment === 'positive';
}

export function isCompletedStripeSignal(payload: StripePayload): boolean {
  const status = payload.data?.object?.status;
  return payload.type === 'stripe_completed' || status === 'paid' || status === 'complete';
}

export function isUnsubscribeSignal(payload: UnsubscribePayload): boolean {
  return Boolean(payload.email) && (payload.reason?.toLowerCase().includes('unsubscribe') ?? true);
}

export function hasProofDefinition(proof?: ProofDefinition): boolean {
  return Boolean(proof?.description && proof.description.trim().length > 0);
}

export function canCreateMissionSync(lead: EchobotLead, payload: RoadmapMissionPayload, opts?: { positive?: boolean; unsubscribe?: boolean }): boolean {
  if (!hasProofDefinition(payload.proofDefinition)) return false;
  if (opts?.unsubscribe) return false;
  const positiveSignal = opts?.positive ?? (lead.replySentiment === 'positive' || Boolean(lead.stripeInvoiceUrl));
  return positiveSignal;
}

export function assertMissionSyncAllowed(lead: EchobotLead, payload: RoadmapMissionPayload, opts?: { positive?: boolean; unsubscribe?: boolean }): void {
  if (!canCreateMissionSync(lead, payload, opts)) {
    throw new Error('Mission sync blocked by policy');
  }
}
