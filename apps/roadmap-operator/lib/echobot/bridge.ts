import { getEchobotStats, getEchobotReviewQueue, getEchobotSyncPreview } from './client';
import {
  mapStats,
  mapLead,
  mapReviewResult,
  mapSyncPreview,
  mapReplyWebhook,
  mapStripeWebhook,
  mapMissionResult,
} from './mapper';
import {
  assertMissionSyncAllowed,
  isPositiveReplySignal,
  isCompletedStripeSignal,
  isUnsubscribeSignal,
} from './policy';
import type { EchobotLead } from '../../../../packages/operator-contracts/src/echobot';
import type { RoadmapSyncPreview, RoadmapSyncResult } from '../../../../packages/operator-contracts/src/roadmap-sync';

export function loadStats() {
  return mapStats(getEchobotStats());
}

export function loadReviewQueue() {
  const queue = getEchobotReviewQueue();
  return {
    generatedAt: queue.generatedAt ?? new Date().toISOString(),
    leads: (queue.leads ?? []).map(mapLead),
  };
}

export function buildSyncPreview(input: EchobotLead): RoadmapSyncPreview {
  const preview = mapSyncPreview(getEchobotSyncPreview(input));
  assertMissionSyncAllowed(preview.lead, preview.payload);
  return preview;
}

function createMissionSync(lead: EchobotLead, opts?: { positive?: boolean; unsubscribe?: boolean; eventId?: string }): RoadmapSyncResult {
  const preview = mapSyncPreview(getEchobotSyncPreview(lead));
  assertMissionSyncAllowed(preview.lead, preview.payload, { positive: opts?.positive, unsubscribe: opts?.unsubscribe });
  return mapMissionResult({
    missionId: opts?.eventId ?? `echobot-${Date.now()}`,
    createdAt: new Date().toISOString(),
    status: opts?.positive ? 'created' : 'queued',
    metadata: {
      eventId: opts?.eventId,
      leadDomain: preview.lead.domain,
    },
  });
}

export function handleReplyWebhook(payload: any) {
  const lead = mapReplyWebhook(payload);
  const positive = isPositiveReplySignal(payload);
  if (!positive) {
    return { status: 'skipped', reason: 'non-positive reply' };
  }
  const result = createMissionSync(lead, { positive, eventId: payload.eventId ?? payload.id });
  return { status: 'created', result };
}

export function handleStripeWebhook(payload: any) {
  const lead = mapStripeWebhook(payload);
  const positive = isCompletedStripeSignal(payload);
  const eventId = payload.data?.object?.id ?? payload.id;
  if (!positive) {
    return { status: 'skipped', reason: 'stripe event not completed' };
  }
  const result = createMissionSync(lead, { positive, eventId });
  return { status: 'created', result };
}

export function handleUnsubscribeWebhook(payload: any) {
  if (!isUnsubscribeSignal(payload)) {
    return { status: 'skipped', reason: 'payload not unsubscribe' };
  }
  return { status: 'blocked', email: payload.email };
}

export function handleMissionSync(payload: EchobotLead, opts?: { positive?: boolean; unsubscribe?: boolean; eventId?: string }) {
  const result = createMissionSync(payload, opts);
  return result;
}
