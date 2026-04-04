import { NextResponse } from "next/server";
import type { EchobotStats } from "@roadmap/operator-contracts";

export async function GET(): Promise<NextResponse> {
  try {
    // TODO: Connect to actual data source (DB or Python service)
    const stats: EchobotStats = {
      total: 0,
      leadsByStatus: {},
      leadsByTruth: {},
      sentiments: {},
      replyRate: 0,
      positiveRate: 0,
      queueSize: 0,
    };

    return NextResponse.json(stats);
  } catch (error) {
    console.error("Error fetching stats:", error);
    return NextResponse.json(
      { error: "Failed to fetch stats" },
      { status: 500 }
    );
  }
}
