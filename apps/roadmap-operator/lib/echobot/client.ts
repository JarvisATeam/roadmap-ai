import { spawnSync } from 'child_process';
import path from 'path';
import type { EchobotStats, EchobotLead } from '../../../../packages/operator-contracts/src/echobot';
import type { RoadmapSyncPreview } from '../../../../packages/operator-contracts/src/roadmap-sync';

const PYTHON_BRIDGE = path.resolve(process.cwd(), 'services/echobot-py/bridge.py');

function runBridge(mode: string, extra?: string[]): string {
  const args = [PYTHON_BRIDGE, mode, ...(extra ?? [])];
  const res = spawnSync('python3', args, { encoding: 'utf-8' });
  if (res.error) throw res.error;
  if (res.status !== 0) throw new Error(res.stderr || `Bridge failed (${mode})`);
  return res.stdout;
}

export function getEchobotStats(): EchobotStats {
  const raw = runBridge('stats');
  return JSON.parse(raw);
}

export function getEchobotReviewQueue(): { leads: EchobotLead[]; generatedAt: string } {
  const raw = runBridge('review');
  return JSON.parse(raw);
}

export function getEchobotSyncPreview(payload: EchobotLead): RoadmapSyncPreview {
  const raw = runBridge('sync', [JSON.stringify(payload)]);
  return JSON.parse(raw);
}
