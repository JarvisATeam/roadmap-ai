/**
 * Symbiosis Layer - Data Contracts
 * 
 * Implementerer "Symbiotic Decision Pillars" og relaterte kontrakter
 * for menneske-AI samskapelse (co-creation).
 */

// ============================================================================
// CORE DECISION PILLARS
// ============================================================================

/**
 * De 8 pilarene i en symbiotisk beslutningskontrakt.
 * Hver AI-leveranse struktureres etter disse feltene.
 */
export interface SymbioticDecisionPillars {
  /** Pilar 1: Krystallklare fakta uten inferens */
  reality: RealityPillar;

  /** Pilar 2: Hva betyr det (operativ, økonomisk, menneskelig betydning) */
  interpretation: InterpretationPillar;

  /** Pilar 3: Hva vet vi ikke - hva kan knuse konklusjonen */
  uncertainty: UncertaintyPillar;

  /** Pilar 4: Hva står på spill - topprisiko ved å ignorere */
  stakes: StakesPillar;

  /** Pilar 5: Hvilke handlingsvalg finnes (A, B, C) */
  choices: ChoicesPillar;

  /** Pilar 6: Hva bør gjøres nå */
  recommendation: RecommendationPillar;

  /** Pilar 7: Hvor dyrt/vanskelig er det å rulle tilbake */
  reversibility: ReversibilityPillar;

  /** Pilar 8: Hvor sterk var menneskets bidrag (0-10) */
  coCreationScore: number;
}

export interface RealityPillar {
  /** Verifiserte fakta uten tolkning */
  facts: string[];
  
  /** Kilder for verifikasjon */
  sources?: string[];
  
  /** Når fakta ble sist verifisert */
  verifiedAt?: string;
}

export interface InterpretationPillar {
  /** Operativ betydning */
  operational: string;
  
  /** Økonomisk betydning */
  economic?: string;
  
  /** Menneskelig/organisatorisk betydning */
  human?: string;
  
  /** Hvorfor dette betyr noe */
  whyThisMatters: string;
}

export interface UncertaintyPillar {
  /** Konfidens-score 0-1 */
  confidenceScore: number;
  
  /** Hva vet vi ikke */
  unknowns: string[];
  
  /** Hva kan knuse konklusjonen */
  dealbreakers: string[];
  
  /** Behov for menneskelig intuisjon */
  requiresHumanIntuition: boolean;
}

export interface StakesPillar {
  /** Risikonivå: low | medium | high | critical */
  riskLevel: RiskLevel;
  
  /** Konkret beskrivelse av hva som står på spill */
  description: string;
  
  /** Kvantifisert risiko (f.eks. EUR, timer, omdømme) */
  quantifiedRisk?: string;
}

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface ChoicesPillar {
  /** Valg A: Standard/anbefalt */
  choiceA: ChoiceOption;
  
  /** Valg B: Alternativ */
  choiceB: ChoiceOption;
  
  /** Valg C: Avventende/escalere */
  choiceC: ChoiceOption;
}

export interface ChoiceOption {
  /** Kort label for valget */
  label: string;
  
  /** Beskrivelse av handling */
  action: string;
  
  /** Forventet utfall */
  expectedOutcome: string;
}

export interface RecommendationPillar {
  /** Anbefalt valg (A, B, eller C) */
  recommendedChoice: "A" | "B" | "C";
  
  /** Begrunnelse for anbefaling */
  reasoning: string;
  
  /** Hvem støtter denne anbefalingen: ai | human | co-created */
  supportedBy: "ai" | "human" | "co-created";
}

export interface ReversibilityPillar {
  /** Score 0-1 (0 = irreversibel, 1 = helt reversibel) */
  score: number;
  
  /** Estimert tid for å rulle tilbake */
  rollbackTime?: string;
  
  /** Estimert kostnad for å rulle tilbake */
  rollbackCost?: string;
  
  /** Angrepunkt - konkret beskrivelse av reverseringsstrategi */
  rollbackStrategy?: string;
}

// ============================================================================
// CHALLENGE PROTOCOL
// ============================================================================

/**
 * Token som representerer en menneskelig korrigering eller utfordring
 * av AI-generert innhold. Lagres for kontinuerlig læring (RLAIF).
 */
export interface SymbioticChallengeToken {
  /** Unik ID for token */
  id: string;
  
  /** Originalt AI-output som ble utfordret */
  originalOutput: string;
  
  /** Menneskelig input/korrigering */
  humanChallenge: string;
  
  /** Type challenge */
  challengeType: ChallengeType;
  
  /** Timestamp for challenge */
  timestamp: string;
  
  /** Vekt basert på emosjonell intensitet og konsekvens */
  weight: number;
  
  /** Kontekst om hva som trigget AI-output */
  context?: ChallengeContext;
  
  /** Eventuell TPM-signatur for verifikasjon (fremtidig) */
  verificationStatus?: VerificationStatus;
}

export type ChallengeType = 
  | "correct"    // Mennesket korrigerer faktisk feil
  | "expand"     // Mennesket ber om utdypning
  | "redirect"   // Mennesket endrer retning
  | "reject";    // Mennesket avviser helt

export interface ChallengeContext {
  /** Opprinnelig query/input */
  originalQuery?: string;
  
  /** Hvilken agent/modul som genererte output */
  sourceAgent?: string;
  
  /** Sesjon ID */
  sessionId?: string;
}

export interface VerificationStatus {
  /** Verifisert, pending, eller avvist */
  status: "verified" | "pending" | "rejected";
  
  /** Metode for verifikasjon */
  method?: "tpm" | "manual" | "auto";
  
  /** Timestamp for verifikasjon */
  verifiedAt?: string;
}

// ============================================================================
// CONTRADICTION & NLI
// ============================================================================

/**
 * Representerer en oppdaget konflikt mellom to kilder/utsagn.
 * Bruker NLI (Natural Language Inference) for deteksjon.
 */
export interface ContradictionPair {
  /** Unik ID */
  id: string;
  
  /** Første utsagn/kilde */
  sourceA: string;
  
  /** Andre utsagn/kilde */
  sourceB: string;
  
  /** NLI-score for kontradiksjon (0-1) */
  contradictionScore: number;
  
  /** Timestamp for deteksjon */
  detectedAt: string;
  
  /** Status: unresolved | resolved_a | resolved_b | both_valid */
  status: ContradictionStatus;
  
  /** Menneskelig resolusjon hvis tilgjengelig */
  humanResolution?: HumanResolution;
}

export type ContradictionStatus = 
  | "unresolved"     // Venter på resolusjon
  | "resolved_a"     // Kilde A valgt
  | "resolved_b"     // Kilde B valgt
  | "both_valid"     // Begge gyldige i ulike kontekster
  | "irrelevant";    // Konflikken er irrelevant

export interface HumanResolution {
  /** Hvilken kilde som ble foretrukket */
  preferredSource: "A" | "B" | "both" | "neither";
  
  /** Begrunnelse for valg */
  reasoning: string;
  
  /** Timestamp */
  resolvedAt: string;
  
  /** Lagres som HumanIntuitionVector */
  intuitionVector?: HumanIntuitionVector;
}

/**
 * Vektoriell representasjon av menneskelig intuisjon.
 * Injiseres i RAG for fremtidige søk.
 */
export interface HumanIntuitionVector {
  /** Unik ID */
  id: string;
  
  /** Intuisjonsinnhold - tekstlig beskrivelse */
  intuition: string;
  
  /** Kontekst der intuisjonen oppstod */
  context: string;
  
  /** Vekting for fremtidig RAG (0-1) */
  weight: number;
  
  /** Kategorier/tags for intuisjonen */
  tags: string[];
  
  /** Timestamp */
  createdAt: string;
  
  /** Referanse til kilde-contradiction hvis relevant */
  sourceContradictionId?: string;
}

// ============================================================================
// MEMORY OF CONSEQUENCE
// ============================================================================

/**
 * Episodisk minne av hendelser og deres konsekvenser.
 * Inkluderer emosjonell og relasjonell resonans.
 */
export interface ConsequenceMemoryEvent {
  /** Unik ID */
  id: string;
  
  /** Hendelsesbeskrivelse */
  event: string;
  
  /** Utfall/konsekvens */
  outcome: string;
  
  /** Magnitude av utfall (0-1) */
  outcomeMagnitude: number;
  
  /** Menneskelig feedback */
  humanFeedback: HumanFeedback;
  
  /** Antall berørte mennesker */
  affectedHumans: number;
  
  /** Timestamp for hendelse */
  occurredAt: string;
  
  /** Time-to-live (TTL) i dager - dynamisk basert på importance score */
  ttlDays: number;
  
  /** Beregnet importance score */
  importanceScore: number;
  
  /** Referanse til relatert challenge token */
  relatedChallengeId?: string;
}

export interface HumanFeedback {
  /** Opplevd stress (0-1) */
  feltStress?: number;
  
  /** Opplevd håp (0-1) */
  feltHope?: number;
  
  /** Opplevd anger/regret (0-1) */
  feltRegret?: number;
  
  /** Empathy index - hvor mye empati ble utvist (0-1) */
  empathyIndex?: number;
  
  /** Fritekst tilbakemelding */
  textFeedback?: string;
}

// ============================================================================
// COGNITIVE COMPRESSION
// ============================================================================

/**
 * Kontrakt for kognitiv kompresjon av kontekst.
 * Tilpasser mengde informasjon basert på brukertilstand.
 */
export interface CompressionConfig {
  /** Nivå: oneline | summary | full */
  level: CompressionLevel;
  
  /** Trigger for kompresjon */
  trigger?: CompressionTrigger;
  
  /** Kort oppsummering (1-2 setninger) */
  oneLine?: string;
  
  /** Medium oppsummering (5 punkter) */
  fivePoints?: string[];
  
  /** Full kontekst */
  fullContext?: string;
}

export type CompressionLevel = "oneline" | "summary" | "full";

export interface CompressionTrigger {
  /** Frustrasjons-index terskel */
  frustrationThreshold: number;
  
  /** Tid brukt på seksjon */
  dwellSeconds?: number;
  
  /** Antall re-reads */
  scrollRepeats?: number;
  
  /** Antall oppklaringsforespørsler */
  followupCount?: number;
}

// ============================================================================
// SYMBIOSIS METRICS
// ============================================================================

/**
 * Samlede metrikker for symbiose-tilstanden mellom menneske og AI.
 */
export interface SymbiosisMetrics {
  /** Co-creation score gjennomsnitt (0-10) */
  averageCoCreationScore: number;
  
  /** Antall challenge tokens */
  totalChallenges: number;
  
  /** Antall uløste konflikter */
  unresolvedContradictions: number;
  
  /** Memory events count */
  memoryEventsCount: number;
  
  /** Trust score basert på feedback */
  trustScore: number;
  
  /** Time-to-decision trend */
  avgTimeToDecision: number;
  
  /** Siste oppdatering */
  lastUpdated: string;
}

// ============================================================================
// API RESPONSE TYPES
// ============================================================================

export interface ChallengeCreateRequest {
  originalOutput: string;
  humanChallenge: string;
  challengeType: ChallengeType;
  context?: ChallengeContext;
}

export interface ChallengeCreateResponse {
  success: boolean;
  token?: SymbioticChallengeToken;
  error?: string;
}

export interface DecisionCreateRequest {
  query: string;
  sourceData?: Record<string, unknown>;
  humanInput?: string;
}

export interface DecisionCreateResponse {
  success: boolean;
  pillars?: SymbioticDecisionPillars;
  formattedOutput?: string;
  error?: string;
}

export interface ContradictionCheckRequest {
  sourceA: string;
  sourceB: string;
}

export interface ContradictionCheckResponse {
  hasContradiction: boolean;
  score: number;
  contradiction?: ContradictionPair;
}
