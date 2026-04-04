import type { EchobotLead } from "./echobot";

export interface ProofDefinition {
  description: string;
  requiredArtifacts?: string[];
}

export interface RoadmapMissionPayload {
  missionTitle: string;
  origin: "echobot" | "manual" | "other";
  proofDefinition: ProofDefinition;
  operatorNotes?: string;
  nextActions: string[];
  metadata?: Record<string, unknown>;
}

export interface RoadmapSyncPreview {
  lead: EchobotLead;
  payload: RoadmapMissionPayload;
}

export type RoadmapSyncStatus = "created" | "queued" | "skipped" | "blocked" | "already_processed";

export interface RoadmapSyncResult {
  missionId: string;
  createdAt: string;
  status: RoadmapSyncStatus;
  metadata?: Record<string, unknown>;
}
