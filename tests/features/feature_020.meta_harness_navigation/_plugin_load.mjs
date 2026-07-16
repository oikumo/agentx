// Test fixture: loads an arbitrary plugin .ts file to verify it parses/imports
// without a SyntaxError (regression guard for the duplicate-`const` defect C1).
//
// Usage: node --experimental-strip-types _plugin_load.mjs <absolute-path.ts>
// Prints "OK" and exits 0 on success; exits 1 with LOAD_ERROR on failure.
import { pathToFileURL } from "node:url"

const p = process.argv[2]
if (!p) {
  console.error("USAGE: _plugin_load.mjs <absolute-path.ts>")
  process.exit(2)
}
try {
  await import(pathToFileURL(p).href)
  console.log("OK")
  process.exit(0)
} catch (e) {
  console.error("LOAD_ERROR: " + (e?.message || String(e)).split("\n")[0])
  process.exit(1)
}
