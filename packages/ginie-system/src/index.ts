/**
 * GenieSystem v1.1.1 - Shell Wrapper + FlowArk Operational Dome
 * Main entry point for the ginie-system package
 */

import { ShellWrapper } from './shell-wrapper';
import { FlowArkDome } from './flowark-dome';

export class GenieSystem {
  private shellWrapper: ShellWrapper;
  private flowArkDome: FlowArkDome;

  constructor() {
    this.shellWrapper = new ShellWrapper();
    this.flowArkDome = new FlowArkDome();
  }

  async initialize(): Promise<void> {
    await this.shellWrapper.initialize();
    await this.flowArkDome.initialize();
  }

  async execute(command: string): Promise<any> {
    const wrappedCommand = this.shellWrapper.wrap(command);
    return await this.flowArkDome.execute(wrappedCommand);
  }

  async shutdown(): Promise<void> {
    await this.flowArkDome.shutdown();
    await this.shellWrapper.cleanup();
  }
}

export { ShellWrapper } from './shell-wrapper';
export { FlowArkDome } from './flowark-dome';
