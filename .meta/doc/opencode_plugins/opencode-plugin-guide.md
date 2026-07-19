# OpenCode Plugin Development Guide

> **Source note:** *What a Plugin Is* through *Examples* are adapted from OpenCode's official plugin docs. *Troubleshooting* compiles patterns reported in OpenCode's GitHub issues (Jan–May 2026) — these describe bugs/behavior at specific versions that may already be fixed upstream, so treat them as diagnostic starting points, not guaranteed current behavior.

## Contents
- [Quick Start](#quick-start)
- [What a Plugin Is](#what-a-plugin-is)
- [Loading a Plugin](#loading-a-plugin)
- [Load Order](#load-order)
- [Anatomy of a Plugin](#anatomy-of-a-plugin)
- [Two Ways Hooks Fire](#two-ways-hooks-fire)
- [TypeScript Support](#typescript-support)
- [External Dependencies](#external-dependencies)
- [Available Events / Hooks](#available-events--hooks)
- [Examples](#examples)
- [Troubleshooting: Known Failure Patterns](#troubleshooting-known-failure-patterns)
- [Pre-Ship Checklist](#pre-ship-checklist)
- [Further Reading](#further-reading)

## Quick Start

The smallest working plugin. Drop this in `.opencode/plugins/hello.js` and restart OpenCode:

```js
// .opencode/plugins/hello.js
export const HelloPlugin = async ({ client }) => {
  await client.app.log({
    body: { service: "hello-plugin", level: "info", message: "Hello plugin loaded!" },
  })

  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        await client.app.log({
          body: { service: "hello-plugin", level: "info", message: `About to run: ${output.args.command}` },
        })
      }
    },
  }
}
```

Restart OpenCode and run any bash tool call — you should see the log line via `opencode --print-logs`. If you don't, jump to [Troubleshooting](#troubleshooting-known-failure-patterns).

Everything below is the full surface area once this basic loop works.

## What a Plugin Is

A plugin is a JavaScript/TypeScript module that exports one or more **plugin functions**. Each function receives a context object and returns an object of hook implementations. Plugins let you hook into OpenCode's events, add custom tools, or modify default behavior — without forking OpenCode itself.

## Loading a Plugin

There are two ways to load a plugin.

### 1. Local files

Place `.js` or `.ts` files in a plugin directory. Files here are loaded automatically at startup — no explicit registration needed.

| Location | Scope |
|---|---|
| `.opencode/plugins/` | Project-level |
| `~/.config/opencode/plugins/` | Global (all projects) |

### 2. From npm

Declare npm packages in your config file:

**`opencode.json`**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["opencode-helicone-session", "opencode-wakatime", "@my-org/custom-plugin"]
}
```

- **Always use an array**, even for one plugin. A repeated `"plugin"` key instead of an array silently drops entries — this is the single most common reason a plugin "just doesn't load."
- Regular and scoped (`@org/name`) npm packages are both supported.
- npm plugins are installed automatically via Bun at startup. Packages and their dependencies are cached in `~/.cache/opencode/node_modules/`.

## Load Order

`global config → project config → global plugin dir → project plugin dir`

All plugins load from all sources, and all hooks run in sequence, in this order:

1. Global config (`~/.config/opencode/opencode.json`)
2. Project config (`opencode.json`)
3. Global plugin directory (`~/.config/opencode/plugins/`)
4. Project plugin directory (`.opencode/plugins/`)

- A duplicate npm package (same name **and** version) loads once, no matter how many sources reference it.
- A local plugin and an npm plugin with a similar name are **not** deduplicated — they load as two separate plugins. If a hook fires twice, this is usually why.

## Anatomy of a Plugin

```js
// .opencode/plugins/example.js
export const MyPlugin = async ({ project, client, $, directory, worktree }) => {
  console.log("Plugin initialized!")

  return {
    // Hook implementations go here
  }
}
```

The plugin function receives a context object:

| Property | Description |
|---|---|
| `project` | Current project information |
| `directory` | Current working directory |
| `worktree` | Git worktree path |
| `client` | OpenCode SDK client — for talking to the AI, logging, etc. |
| `$` | Bun's shell API — for running commands |

## Two Ways Hooks Fire

Worth knowing before you pick an event — it changes how you write the handler.

**1. Direct hooks** — a dedicated method, called with its own `(input, output)` signature. These can intercept and mutate behavior, not just observe it:

```js
return {
  "tool.execute.before": async (input, output) => { /* throw to block, or mutate output.args */ },
  "tool.execute.after": async (input, output) => { /* ... */ },
  "shell.env": async (input, output) => { /* mutate output.env */ },
  "experimental.session.compacting": async (input, output) => { /* mutate output.context or output.prompt */ },
}
```

**2. The generic event bus** — a single `event` method fires for everything OpenCode emits; you branch on `event.type`:

```js
return {
  event: async ({ event }) => {
    if (event.type === "session.idle") { /* ... */ }
  },
}
```

The official examples only demonstrate `session.*` (and similar) events through the generic `event` bus, never as direct named keys. For anything in the categorized list below other than `tool.execute.before/after`, `shell.env`, or `experimental.session.compacting`, start with the `event` bus pattern — and check the `@opencode-ai/plugin` type definitions if you want to confirm a direct-key variant also exists.

## TypeScript Support

```ts
// my-plugin.ts
import type { Plugin } from "@opencode-ai/plugin"

export const MyPlugin: Plugin = async ({ project, client, $, directory, worktree }) => {
  return {
    // Type-safe hook implementations
  }
}
```

## External Dependencies

Local plugins and custom tools can use external npm packages. Add a `package.json` inside your config directory:

**`.opencode/package.json`**
```json
{
  "dependencies": {
    "shescape": "^2.1.0"
  }
}
```

OpenCode runs `bun install` at startup to install these; your plugins and tools can then import them normally:

```ts
// .opencode/plugins/my-plugin.ts
import { escape } from "shescape"

export const MyPlugin = async (ctx) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "bash") {
        output.args.command = escape(output.args.command)
      }
    },
  }
}
```

> **Linux gotcha:** if a dependency (or one of *its* dependencies) ships a native binary — e.g. `sharp` — it needs to be compiled for `linux-x64` specifically. OpenCode's isolated plugin install directory doesn't always trigger this the way a normal project-local `npm install` does. See [Troubleshooting](#troubleshooting-known-failure-patterns).

## Available Events / Hooks

| Category | Events |
|---|---|
| Command | `command.executed` |
| File | `file.edited`, `file.watcher.updated` |
| Installation | `installation.updated` |
| LSP | `lsp.client.diagnostics`, `lsp.updated` |
| Message | `message.part.removed`, `message.part.updated`, `message.removed`, `message.updated` |
| Permission | `permission.asked`, `permission.replied` |
| Server | `server.connected` |
| Session | `session.created`, `session.compacted`, `session.deleted`, `session.diff`, `session.error`, `session.idle`, `session.status`, `session.updated` |
| Todo | `todo.updated` |
| Shell | `shell.env` |
| Tool | `tool.execute.before`, `tool.execute.after` |
| TUI | `tui.prompt.append`, `tui.command.execute`, `tui.toast.show` |

Exact input/output payload shape per event isn't fully spelled out in the docs — when in doubt, log the raw payload once via `client.app.log()` to inspect it before building logic around it.

## Examples

### Send a notification on session completion

macOS (uses AppleScript via `osascript`):

```js
// .opencode/plugins/notification.js
export const NotificationPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`osascript -e 'display notification "Session completed!" with title "opencode"'`
      }
    },
  }
}
```

Linux equivalent (uses `notify-send`, part of `libnotify-bin` on Debian/Ubuntu, `libnotify` on Fedora/Arch):

```js
// .opencode/plugins/notification.js
export const NotificationPlugin = async ({ project, client, $, directory, worktree }) => {
  return {
    event: async ({ event }) => {
      if (event.type === "session.idle") {
        await $`notify-send "opencode" "Session completed!"`
      }
    },
  }
}
```

> Note: OpenCode Desktop can send system notifications automatically on response-ready or session-error events, without a custom plugin. This pattern is mainly for the CLI/TUI, or custom notification logic (e.g. routing to Slack instead).

### Block reads of `.env` files

```js
// .opencode/plugins/env-protection.js
export const EnvProtection = async ({ project, client, $, directory, worktree }) => {
  return {
    "tool.execute.before": async (input, output) => {
      if (input.tool === "read" && output.args.filePath.includes(".env")) {
        throw new Error("Do not read .env files")
      }
    },
  }
}
```

### Inject environment variables into all shell execution

```js
// .opencode/plugins/inject-env.js
export const InjectEnvPlugin = async () => {
  return {
    "shell.env": async (input, output) => {
      output.env.MY_API_KEY = "secret"
      output.env.PROJECT_ROOT = input.cwd
    },
  }
}
```

### Add a custom tool

```ts
// .opencode/plugins/custom-tools.ts
import { type Plugin, tool } from "@opencode-ai/plugin"

export const CustomToolsPlugin: Plugin = async (ctx) => {
  return {
    tool: {
      mytool: tool({
        description: "This is a custom tool",
        args: {
          foo: tool.schema.string(),
        },
        async execute(args, context) {
          const { directory, worktree } = context
          return `Hello ${args.foo} from ${directory} (worktree: ${worktree})`
        },
      }),
    },
  }
}
```

`tool()` builds a custom tool OpenCode can call:

- `description` — what the tool does
- `args` — Zod schema for the tool's arguments
- `execute` — function run when the tool is invoked

Custom tools sit alongside built-in tools. **If a plugin tool shares a name with a built-in tool, the plugin tool wins.**

### Structured logging

Use `client.app.log()` instead of `console.log` — it's what shows up in `opencode --print-logs`, which matters once you're debugging a plugin that isn't behaving:

```ts
// .opencode/plugins/my-plugin.ts
export const MyPlugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "my-plugin",
      level: "info",
      message: "Plugin initialized",
      extra: { foo: "bar" },
    },
  })
}
```

Log levels: `debug`, `info`, `warn`, `error`.

### Compaction hooks

Customize the context injected when a session is compacted. Fires **before** the LLM generates a continuation summary.

**Append custom context:**

```ts
// .opencode/plugins/compaction.ts
import type { Plugin } from "@opencode-ai/plugin"

export const CompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.context.push(`
## Custom Context

Include any state that should persist across compaction:
- Current task status
- Important decisions made
- Files being actively worked on
`)
    },
  }
}
```

**Fully replace the compaction prompt:**

```ts
// .opencode/plugins/custom-compaction.ts
import type { Plugin } from "@opencode-ai/plugin"

export const CustomCompactionPlugin: Plugin = async (ctx) => {
  return {
    "experimental.session.compacting": async (input, output) => {
      output.prompt = `
You are generating a continuation prompt for a multi-agent swarm session.

Summarize:
1. The current task and its status
2. Which files are being modified and by whom
3. Any blockers or dependencies between agents
4. The next steps to complete the work

Format as a structured prompt that a new agent can use to resume work.
`
    },
  }
}
```

> Setting `output.prompt` fully overrides the default compaction message — `output.context` is ignored in that case. Use one or the other, not both.

## Troubleshooting: Known Failure Patterns

Start by running `opencode --print-logs` and grepping for `service=plugin` — the log line usually points at one of these.

| Symptom | Likely cause | Fix |
|---|---|---|
| Plugin silently missing, no error | Duplicate `"plugin"` key in `opencode.json` instead of an array | Use `"plugin": ["a", "b"]` |
| Plugin shows old version / stale behavior after upgrading OpenCode | Stale Bun cache | `rm -rf ~/.cache/opencode/node_modules` and restart |
| `"No plugin targets found"` after `opencode upgrade` | Plugin's export shape doesn't match what the new OpenCode version expects | Check the plugin's changelog for compatibility with your `opencode-ai` version, or pin OpenCode back temporarily |
| `Missing 'default' export` error pointing into a dependency (e.g. `sharp`) under `~/.cache/opencode/packages/...` | A transitive native-module dependency wasn't compiled for `linux-x64` in the isolated plugin install dir | Report to the plugin author (native deps can often be made optional); check if a "slim" variant without the native dep exists |
| Local plugin (`.opencode/plugins/`) importing an npm package fails to resolve it, even though it's in the project's `node_modules` | Bun's module resolution starts from the plugin subdirectory, not the project root | Symlink `node_modules` into `.opencode/plugins/`, or move the dependency into an npm-published plugin instead of a local file |
| Plugin "installs successfully" per logs, but nothing changes | Installed to the wrong directory (e.g. a `~/.opencode/` binary-install dir instead of `~/.config/opencode/`) | Confirm the plugin file/config actually sits under `~/.config/opencode/` (global) or `.opencode/` (project) |
| Everything looks right, still nothing fires | Used a direct key for an event only supported via the generic bus, or vice versa | Re-check [Two Ways Hooks Fire](#two-ways-hooks-fire) |

## Pre-Ship Checklist

1. Decide scope: project-only (`.opencode/plugins/`) vs global (`~/.config/opencode/plugins/`) vs published npm package.
2. Pick the hook(s) you need — direct key or event-bus, per [Two Ways Hooks Fire](#two-ways-hooks-fire).
3. If you need external npm deps: local plugin → add `.opencode/package.json`; distributable plugin → publish to npm, declaring `@opencode-ai/plugin` as a peer dependency rather than bundling it.
4. Use `client.app.log()`, not `console.log`, so output shows up in `--print-logs`.
5. If a custom tool intentionally shadows a built-in tool name, do it deliberately, not by accident.
6. Test locally (drop the file in `.opencode/plugins/`) before publishing to npm.
7. On Linux: avoid macOS-only shell calls (`osascript`) — use `notify-send` or similar, and watch for native-module dependencies that may not build in the isolated plugin install path.
8. Before filing a bug: reproduce with `opencode --print-logs`, and check whether clearing `~/.cache/opencode/node_modules` fixes it first — this resolves a large share of "broke after upgrade" reports.

## Further Reading

- Official plugin docs: https://opencode.ai/docs/plugins/
- Config reference: https://opencode.ai/docs/config/
- Troubleshooting: https://opencode.ai/docs/troubleshooting/
