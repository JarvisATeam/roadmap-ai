export interface RoadmapMissionPayload {
  missionTitle: string;
  origin: 'echobot' | 'manual' | 'other';
  proofDefinition: string;
  operatorNotes?: string;
  nextActions: string[];
  metadata?: Record<string, unknown>;
}

export interface RoadmapSyncResult {
  missionId: string;
  createdAt: string;
  status: 'created' | 'queued' | 'skipped';
}
