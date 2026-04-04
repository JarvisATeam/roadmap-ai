export type Lead = {
  id: string;
  companyName: string;
  contactEmail: string;
  hookType?: string;
  status: 'pending' | 'approved' | 'rejected';
};

export type MissionDraft = {
  title: string;
  proofDefinition: string;
  nextActions: string[];
};
