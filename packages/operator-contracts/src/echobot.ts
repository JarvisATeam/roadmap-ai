export interface EchobotLead {
  domain: string;
  companyName: string;
  contactEmail: string;
  contactName: string;
  hypothesis: string;
  hookType: string;
  compressedTimeline: string;
  draftSubject: string;
  draftBody: string;
  evidenceUrl?: string;
  confidenceScore: number;
  truthStatus: 'PASSED' | 'FAILED' | 'PENDING';
  sendStatus: 'QUEUE' | 'APPROVED' | 'REJECTED' | 'SENT';
  replySentiment?: string;
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

export interface EchobotReviewQueue {
  leads: EchobotLead[];
  generatedAt: string;
}

export interface EchobotSyncPreview {
  lead: EchobotLead;
  missionTitle: string;
  nextActions: string[];
  proofDefinition: string;
  operatorNotes?: string;
}

export interface EchobotPolicy {
  maxCohortSize: number;
  manualApprovalRequired: boolean;
  requiresProofDefinition: boolean;
  syncRequiresPositiveSignal: boolean;
}
