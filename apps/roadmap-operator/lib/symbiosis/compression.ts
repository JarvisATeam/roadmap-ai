/**
 * Symbiosis Compression Module
 * 
 * Gir 1-linje / 5-punkt / full kontekst etter belastning.
 * Tilpasser informasjonsmengde basert på bruker-tilstand.
 */

import {
  CompressionConfig,
  CompressionLevel,
  CompressionTrigger,
} from "@roadmap/operator-contracts";

/**
 * Bruker telemetri for kognitiv load
 */
export interface UserTelemetry {
  /** Antall re-reads av samme seksjon */
  scrollRepeats: number;
  
  /** Tid brukt på seksjon (sekunder) */
  dwellSeconds: number;
  
  /** Antall oppklaringsforespørsler */
  followupCount: number;
  
  /** EMA (exponential moving average) av frustrasjon */
  frustrationIndex: number;
  
  /** Bruker-nivå */
  userLevel: "novice" | "intermediate" | "expert";
}

/**
 * Compression Controller
 */
export class CompressionController {
  private defaultTrigger: CompressionTrigger = {
    frustrationThreshold: 0.65,
    dwellSeconds: 60,
    scrollRepeats: 2,
    followupCount: 1,
  };

  /**
   * Velger kompresjonsnivå basert på telemetri
   */
  selectLevel(telemetry: UserTelemetry): CompressionLevel {
    // Expert-brukere får alltid full kontekst
    if (telemetry.userLevel === "expert") {
      return "full";
    }

    // Sjekk frustrasjons-index
    if (telemetry.frustrationIndex > this.defaultTrigger.frustrationThreshold) {
      return "oneline";
    }

    // Sjekk scroll repeats (sterkt signal for usikkerhet)
    if (telemetry.scrollRepeats >= (this.defaultTrigger.scrollRepeats || 2)) {
      return "summary";
    }

    // Sjekk dwell time
    if (telemetry.dwellSeconds > (this.defaultTrigger.dwellSeconds || 60)) {
      return "summary";
    }

    // Sjekk followup requests
    if (telemetry.followupCount >= (this.defaultTrigger.followupCount || 1)) {
      return "oneline";
    }

    return "full";
  }

  /**
   * Kompreser tekst til ønsket nivå
   */
  compress(text: string, level: CompressionLevel): CompressionConfig {
    switch (level) {
      case "oneline":
        return {
          level,
          oneLine: this.toOneLine(text),
        };
      
      case "summary":
        return {
          level,
          oneLine: this.toOneLine(text),
          fivePoints: this.toFivePoints(text),
        };
      
      case "full":
      default:
        return {
          level,
          oneLine: this.toOneLine(text),
          fivePoints: this.toFivePoints(text),
          fullContext: text,
        };
    }
  }

  /**
   * Auto-komprimerer basert på telemetri
   */
  autoCompress(text: string, telemetry: UserTelemetry): CompressionConfig {
    const level = this.selectLevel(telemetry);
    return this.compress(text, level);
  }

  /**
   * Konverterer til 1-linje
   */
  private toOneLine(text: string): string {
    // Ta første setning, maks 150 tegn
    const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
    if (sentences.length === 0) return text.substring(0, 150);
    
    const first = sentences[0].trim();
    return first.length > 150 ? first.substring(0, 147) + "..." : first;
  }

  /**
   * Konverterer til 5 punkter
   */
  private toFivePoints(text: string): string[] {
    // Del i setninger og velg de viktigste
    const sentences = text
      .split(/[.!?]+/)
      .map(s => s.trim())
      .filter(s => s.length > 10 && s.length < 200);

    // Prioriter setninger med nøkkelord
    const priorityWords = [
      "anbefaler", "bør", "må", "viktig", "kritisk",
      "recommend", "should", "must", "important", "critical"
    ];

    const scored = sentences.map(s => {
      const lower = s.toLowerCase();
      const score = priorityWords.reduce((acc, word) => 
        lower.includes(word) ? acc + 1 : acc, 0
      );
      return { sentence: s, score };
    });

    // Sorter etter score, ta top 5
    scored.sort((a, b) => b.score - a.score);
    
    const points = scored.slice(0, 5).map(s => s.sentence);
    
    // Fyll på hvis vi har færre enn 5
    while (points.length < 5 && sentences.length > points.length) {
      const remaining = sentences.filter(s => !points.includes(s));
      if (remaining.length > 0) {
        points.push(remaining[0]);
      } else {
        break;
      }
    }

    return points;
  }

  /**
   * Beregner frustrasjons-index fra rå signaler
   */
  calculateFrustrationIndex(signals: {
    scrollRepeats: number;
    dwellSeconds: number;
    clarificationRequests: number;
  }): number {
    // Scroll repeats er sterkest signal
    const scrollFactor = Math.min(signals.scrollRepeats / 5, 1) * 0.4;
    
    // Time on section er nest sterkest
    const timeFactor = Math.min(signals.dwellSeconds / 120, 1) * 0.3;
    
    // Clarification requests
    const clarifyFactor = Math.min(signals.clarificationRequests / 3, 1) * 0.3;

    return Math.min(scrollFactor + timeFactor + clarifyFactor, 1);
  }
}

// Export singleton
export const compressionController = new CompressionController();

/**
 * Formatter compression for visning
 */
export function formatCompression(config: CompressionConfig): string {
  const lines: string[] = [];
  
  lines.push(`=== ${config.level.toUpperCase()} KOMPRESJON ===\n`);
  
  if (config.oneLine) {
    lines.push("📌 Oppsummering:");
    lines.push(config.oneLine);
    lines.push("");
  }
  
  if (config.fivePoints) {
    lines.push("📋 Hovedpunkter:");
    config.fivePoints.forEach((point, i) => {
      lines.push(`  ${i + 1}. ${point}`);
    });
    lines.push("");
  }
  
  if (config.fullContext) {
    lines.push("📖 Full kontekst:");
    lines.push(config.fullContext);
  }
  
  return lines.join("\n");
}

/**
 * Demo telemetri-data
 */
export const demoTelemetry: Record<string, UserTelemetry> = {
  relaxed: {
    scrollRepeats: 0,
    dwellSeconds: 10,
    followupCount: 0,
    frustrationIndex: 0.1,
    userLevel: "intermediate",
  },
  uncertain: {
    scrollRepeats: 2,
    dwellSeconds: 45,
    followupCount: 0,
    frustrationIndex: 0.4,
    userLevel: "intermediate",
  },
  frustrated: {
    scrollRepeats: 4,
    dwellSeconds: 90,
    followupCount: 2,
    frustrationIndex: 0.75,
    userLevel: "intermediate",
  },
  expert: {
    scrollRepeats: 0,
    dwellSeconds: 5,
    followupCount: 0,
    frustrationIndex: 0,
    userLevel: "expert",
  },
};
