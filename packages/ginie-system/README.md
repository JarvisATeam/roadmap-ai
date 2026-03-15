# GenieSystem v1.1.1

## Shell Wrapper + FlowArk Operational Dome

GenieSystem is a TypeScript package that provides shell command wrapping and operational workflow management through a protected dome environment.

## Features

- **Shell Wrapper**: Safe execution of shell commands with logging and error handling
- **FlowArk Operational Dome**: Manages workflow operations with queuing and tracking
- **TypeScript Support**: Full type definitions included
- **Async/Await**: Modern promise-based API

## Installation

```bash
npm install @roadmap-ai/ginie-system
```

## Usage

```typescript
import { GenieSystem } from '@roadmap-ai/ginie-system';

const genie = new GenieSystem();
await genie.initialize();

const result = await genie.execute('echo "Hello World"');
console.log(result);

await genie.shutdown();
```

## API

### GenieSystem

Main class that orchestrates shell wrapper and FlowArk dome.

- `initialize()`: Initialize the system
- `execute(command: string)`: Execute a command
- `shutdown()`: Clean shutdown

### ShellWrapper

Handles shell command execution.

- `wrap(command: string)`: Wrap command with safety checks
- `execute(command: string)`: Execute wrapped command

### FlowArkDome

Manages operational workflows.

- `execute(command: string)`: Execute within dome
- `getOperation(id: string)`: Get operation status
- `getAllOperations()`: Get all operations

## License

MIT
