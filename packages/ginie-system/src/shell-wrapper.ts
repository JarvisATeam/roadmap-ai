/**
 * Shell Wrapper Module
 * Provides shell command wrapping functionality for GenieSystem
 */

import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface ShellConfig {
  timeout?: number;
  env?: Record<string, string>;
  cwd?: string;
}

export class ShellWrapper {
  private config: ShellConfig;
  private isInitialized: boolean = false;

  constructor(config: ShellConfig = {}) {
    this.config = {
      timeout: 30000,
      ...config
    };
  }

  async initialize(): Promise<void> {
    this.isInitialized = true;
    console.log('ShellWrapper initialized');
  }

  wrap(command: string): string {
    // Wrap command with safety checks and logging
    return `set -e; echo "[ShellWrapper] Executing: ${command}"; ${command}`;
  }

  async execute(command: string): Promise<{ stdout: string; stderr: string }> {
    if (!this.isInitialized) {
      throw new Error('ShellWrapper not initialized');
    }

    try {
      const wrappedCommand = this.wrap(command);
      const result = await execAsync(wrappedCommand, {
        timeout: this.config.timeout,
        env: { ...process.env, ...this.config.env },
        cwd: this.config.cwd
      });
      return result;
    } catch (error: any) {
      throw new Error(`Shell execution failed: ${error.message}`);
    }
  }

  async cleanup(): Promise<void> {
    this.isInitialized = false;
    console.log('ShellWrapper cleaned up');
  }
}
