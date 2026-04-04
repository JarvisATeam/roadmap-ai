export type EchobotTruthStatus = "PASSED" | "FAILED" | "PENDING";
export type EchobotSendStatus = "QUEUE" | "APPROVED" | "REJECTED" | "SENT";
export type EchobotReplySentiment = "positive" | "neutral" | "negative" | "unknown";

export interface TruthCheckResult {
  status: EchobotTruthStatus;
  confidenceScore: number;
  evidenceUrl?: string;
  evidenceSummary?: string;
  hypothesis?: string;
}

export interface EchobotLead {
  id?: string;
  domain: string;
  companyName: string;
  contactEmail: string;
  contactName?: string;
  hypothesis: string;
  hookType?: string;
  compressedTimeline?: string;
  draftSubject?: string;
  draftBody?: string;
  evidenceUrl?: string;
  confidenceScore: number;
  truthStatus: EchobotTruthStatus;
  sendStatus: EchobotSendStatus;
  replySentiment?: EchobotReplySentiment;
  stripeInvoiceUrl?: string;
  optedOut?: boolean;
  createdAt?: string;
}

export interface EchobotStats {
  total: number;
  leadsByStatus: Record<string, number>;
  leadsByTruth: Record<string, number>;
  sentiments: Record<string, number>;
  replyRate: number;
  positiveRate: number;
  queueSize: number;
}

export interface EchobotReviewResult {
  lead: EchobotLead;
  truth: TruthCheckResult;
  approved: boolean;
  reviewerNotes?: string;
}

export interface EchobotPolicy {
  maxCohortSize: number;
  manualApprovalRequired: boolean;
  requiresProofDefinition: boolean;
  syncRequiresPositiveSignal: boolean;
}
