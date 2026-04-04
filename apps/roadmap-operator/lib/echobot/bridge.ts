import { getEchobotStats, getEchobotReviewQueue, getEchobotSyncPreview } from './client';
import { mapStats, mapLead, mapReviewResult, mapSyncPreview } from './mapper';
import { assertSyncAllowed } from './policy';
import type { EchobotLead } from '../../../../packages/operator-contracts/src/echobot';
import type { RoadmapSyncPreview } from '../../../../packages/operator-contracts/src/roadmap-sync';

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
  assertSyncAllowed(preview.lead, preview.payload);
  return preview;
}
