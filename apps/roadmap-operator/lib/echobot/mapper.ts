import type {
  EchobotLead,
  EchobotStats,
  EchobotReviewResult,
  TruthCheckResult,
} from '../../../../packages/operator-contracts/src/echobot';
import type {
  RoadmapMissionPayload,
  RoadmapSyncPreview,
  RoadmapSyncResult,
} from '../../../../packages/operator-contracts/src/roadmap-sync';

export function mapStats(raw: any): EchobotStats {
  return {
    total: raw.total ?? 0,
    leadsByStatus: raw.leadsByStatus ?? raw.leads_by_status ?? {},
    leadsByTruth: raw.leadsByTruth ?? raw.leads_by_truth ?? {},
    sentiments: raw.sentiments ?? {},
    replyRate: raw.replyRate ?? 0,
    positiveRate: raw.positiveRate ?? 0,
    queueSize: raw.queueSize ?? 0,
  };
}

export function mapLead(raw: any): EchobotLead {
  return {
    domain: raw.domain ?? raw.company?.domain ?? '',
    companyName: raw.companyName ?? raw.company_name ?? '',
    contactEmail: raw.contactEmail ?? raw.contact_email ?? '',
    contactName: raw.contactName ?? raw.contact_name ?? '',
    hypothesis: raw.hypothesis ?? '',
    hookType: raw.hookType ?? raw.hook_type,
    compressedTimeline: raw.compressedTimeline ?? raw.compressed_timeline,
    draftSubject: raw.draftSubject ?? raw.draft_subject,
    draftBody: raw.draftBody ?? raw.draft_body,
    evidenceUrl: raw.evidenceUrl ?? raw.evidence_url,
    confidenceScore: raw.confidenceScore ?? raw.confidence_score ?? 0,
    truthStatus: raw.truthStatus ?? raw.truth_status ?? 'PENDING',
    sendStatus: raw.sendStatus ?? raw.send_status ?? 'QUEUE',
    replySentiment: raw.replySentiment ?? raw.reply_sentiment ?? 'unknown',
    stripeInvoiceUrl: raw.stripeInvoiceUrl ?? raw.stripe_invoice_url,
    optedOut: Boolean(raw.optedOut ?? raw.opted_out),
    createdAt: raw.createdAt ?? raw.created_at,
  };
}

export function mapTruth(raw: any): TruthCheckResult {
  return {
    status: raw.status ?? raw.truth_status ?? 'PENDING',
    confidenceScore: raw.confidenceScore ?? raw.confidence_score ?? 0,
    evidenceUrl: raw.evidenceUrl ?? raw.evidence_url,
    evidenceSummary: raw.evidenceSummary ?? raw.evidence_summary,
    hypothesis: raw.hypothesis,
  };
}

export function mapReviewResult(raw: any): EchobotReviewResult {
  return {
    lead: mapLead(raw.lead ?? raw),
    truth: mapTruth(raw.truth ?? raw),
    approved: Boolean(raw.approved ?? raw.isApproved),
    reviewerNotes: raw.notes ?? raw.reviewerNotes,
  };
}

export function mapMissionPayload(raw: any): RoadmapMissionPayload {
  return {
    missionTitle: raw.missionTitle ?? 'Echobot follow-up',
    origin: raw.origin ?? 'echobot',
    proofDefinition: raw.proofDefinition ?? { description: 'Lead verified', requiredArtifacts: [] },
    operatorNotes: raw.operatorNotes ?? '',
    nextActions: raw.nextActions ?? [],
    metadata: raw.metadata ?? {},
  };
}

export function mapSyncPreview(raw: any): RoadmapSyncPreview {
  return {
    lead: mapLead(raw.lead ?? raw.payload?.lead ?? raw),
    payload: mapMissionPayload(raw.payload ?? raw),
  };
}

export function mapReplyWebhook(raw: any): EchobotLead {
  const lead = raw.lead ?? raw;
  return mapLead({
    ...lead,
    replySentiment: lead.replySentiment ?? lead.sentiment ?? 'unknown',
  });
}

export function mapStripeWebhook(raw: any): EchobotLead {
  const lead = raw.lead ?? raw;
  return mapLead({
    ...lead,
    stripeInvoiceUrl: lead.stripeInvoiceUrl ?? lead.invoiceUrl ?? lead.invoice_url ?? '',
    replySentiment: lead.replySentiment ?? 'positive',
  });
}

export function mapMissionResult(raw: any): RoadmapSyncResult {
  return {
    missionId: raw.missionId ?? raw.mission_id ?? 'pending',
    createdAt: raw.createdAt ?? raw.created_at ?? new Date().toISOString(),
    status: raw.status ?? 'queued',
  };
}
