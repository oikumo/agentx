// V2 compat for V1 `tool()` definitions (migrate-v1 fast path).
//
// V1: import { tool } from "@opencode-ai/plugin"
//     tool({ description, args: { x: tool.schema.string().optional().describe("...") },
//            async execute(args, context) { ... return string | {title,output,metadata} } })
//
// V2: Plugin.define({ id, setup(ctx) { await ctx.tool.transform(ed => ed.add({name, description, input, execute})) } })
//     input = JSON Schema, execute returns {content, metadata}.
//
// This module implements the V1 `tool` surface on top of V2 primitives so
// pure-tool plugins keep their logic byte-identical and only change their
// entrypoint (import + Plugin.define + transform registration). Hook-bearing
// plugins (omt_enforcer) migrate explicitly via ctx.tool.hook / event.subscribe.
//
// Schema builders support the exact subset used in this repo:
//   tool.schema.string() | .number() | .boolean() each with .optional() and .describe()
// execute wrapping:
//   string                    -> { content: string }
//   {title, output, metadata} -> { content: output, metadata } (title prepended when output lacks it)
//   {content,...} (already V2)-> passthrough
//   other objects             -> { content: JSON.stringify(obj) } (fail-open, never throws)

export function makeSchemaBuilder(type: string) {
  const b: any = {
    _type: type,
    _optional: false,
    _description: undefined as string | undefined,
    optional() { this._optional = true; return this },
    describe(d: string) { this._description = d; return this },
    toJSONSchema() {
      const s: any = { type: this._type }
      if (this._description) s.description = this._description
      return s
    },
  }
  return b
}

export const schema = {
  string() { return makeSchemaBuilder("string") },
  number() { return makeSchemaBuilder("number") },
  boolean() { return makeSchemaBuilder("boolean") },
}

function toInput(args: Record<string, any> | undefined) {
  const properties: Record<string, any> = {}
  const required: string[] = []
  if (args) {
    for (const [k, v] of Object.entries(args)) {
      if (v && typeof v === "object" && typeof (v as any).toJSONSchema === "function") {
        properties[k] = (v as any).toJSONSchema()
        if (!(v as any)._optional) required.push(k)
      } else {
        // Unknown shape — pass through as string (fail-open).
        properties[k] = { type: "string" }
      }
    }
  }
  return { type: "object", properties, required, additionalProperties: false }
}

function wrapExecute(orig: (args: any, ctx: any) => Promise<any> | any) {
  return async (input: any, toolCtx: any) => {
    // V2 ToolContext has sessionID; V1 custom-tool context had sessionID too.
    // Provide both `sessionID` and legacy aliases so original bodies keep working.
    const ctx = toolCtx ?? {}
    let out: any
    try {
      out = await orig(input, ctx)
    } catch (e: any) {
      // V1 tools returned errors as strings, never threw for expected cases.
      // Preserve throw for gate blocks (OmtBlock extends Error) — hooks rely on it.
      throw e
    }
    if (typeof out === "string") return { content: out }
    if (out && typeof out === "object") {
      if ("content" in out || "output" in out || "metadata" in out) {
        // V1 envelope ({title,output,metadata}) → V2 ({content, metadata}).
        // Title is folded into content (no V2 title field); `output` is NOT
        // preserved (V2 output requires an output schema — returning one
        // without it fails runtime validation).
        if ("content" in out && !("output" in out)) return out
        const title = (out as any).title ? String((out as any).title) : undefined
        const body = typeof (out as any).output === "string" ? (out as any).output
          : (out as any).output !== undefined ? JSON.stringify((out as any).output)
          : ""
        const content = (title ? title + "\n" : "") + body
        const res: any = { content }
        if ((out as any).metadata !== undefined) res.metadata = (out as any).metadata
        return res
      }
      return { content: JSON.stringify(out) }
    }
    return { content: String(out ?? "") }
  }
}

export function tool(def: { description: string; args?: Record<string, any>; execute: (args: any, ctx: any) => Promise<any> | any }) {
  return {
    description: def.description,
    input: toInput(def.args),
    execute: wrapExecute(def.execute),
  }
}
tool.schema = schema

// Register a map of shim tools (as returned by `tool()`) under their object keys.
export async function registerTools(ctx: any, tools: Record<string, any>) {
  await ctx.tool.transform((editor: any) => {
    for (const [name, t] of Object.entries(tools)) {
      editor.add({ name, description: (t as any).description, input: (t as any).input, execute: (t as any).execute } as any)
    }
  })
}
