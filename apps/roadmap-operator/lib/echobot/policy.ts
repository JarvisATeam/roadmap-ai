import type { EchobotReviewResult, EchobotLead } from '../../../../packages/operator-contracts/src/echobot';
import type { RoadmapMissionPayload } from '../../../../packages/operator-contracts/src/roadmap-sync';

export function canApproveReview(review: EchobotReviewResult): boolean {
  return review.truth.status === 'PASSED' && review.truth.confidenceScore >= 0.7;
}

export function canSyncMission(lead: EchobotLead, payload: RoadmapMissionPayload): boolean {
  const hasPositiveSignal = lead.replySentiment === 'positive' || Boolean(lead.stripeInvoiceUrl);
  const hasProof = Boolean(payload.proofDefinition?.description);
  return hasPositiveSignal && hasProof;
}

export function assertSyncAllowed(lead: EchobotLead, payload: RoadmapMissionPayload): void {
  if (!canSyncMission(lead, payload)) {
    throw new Error('Echobot sync blocked: missing positive signal or proof definition.');
  }
}
