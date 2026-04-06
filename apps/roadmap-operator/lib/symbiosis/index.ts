/**
 * Symbiosis Layer - Core Modules
 * 
 * Sidecar-lag for menneske-AI samskapelse (co-creation) i Roadmap-AI.
 * Integreres oppå eksisterende ECHOBOT/roadmap-operator kjerne.
 */

// Challenge Protocol
export {
  ChallengeManager,
  ChallengeStore,
  challengeManager,
  challengeStore,
  isChallengeWindowOpen,
  formatChallenge,
} from "./challenge";

export type { ChallengeConfig } from "./challenge";

// Decision Pillars
export {
  DecisionFormatter,
  decisionFormatter,
  handleDecisionRequest,
  formatEchobotReviewToPillars,
} from "./decision";

export type { DecisionInput } from "./decision";

// Contradiction Detection
export {
  ContradictionDetector,
  contradictionDetector,
  contradictionStore,
  checkMultipleSources,
  formatContradiction,
} from "./contradiction";

export type { ContradictionConfig } from "./contradiction";

// Memory of Consequence
export {
  MemoryManager,
  MemoryStore,
  memoryManager,
  memoryStore,
  formatMemory,
} from "./memory";

export type { MemoryConfig } from "./memory";

// Cognitive Compression
export {
  CompressionController,
  compressionController,
  formatCompression,
  demoTelemetry,
} from "./compression";

export type { UserTelemetry } from "./compression";

// Types re-export for convenience
export type {
  SymbioticDecisionPillars,
  SymbioticChallengeToken,
  ConsequenceMemoryEvent,
  ContradictionPair,
  HumanIntuitionVector,
  CompressionConfig,
  ChallengeType,
  ChallengeContext,
  DecisionCreateRequest,
  DecisionCreateResponse,
  ContradictionCheckRequest,
  ContradictionCheckResponse,
} from "@roadmap/operator-contracts";
