import { fileURLToPath } from 'node:url';
import { resolve, join } from 'node:path';
import { promises as fs } from 'node:fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = resolve(__filename, '..');
const REPO_ROOT = resolve(__dirname, '../../..');

const enforcerMod = await import(resolve(REPO_ROOT, '.opencode/plugin/omt_enforcer.ts'));
const dollarStub = () => { throw new Error('unexpected'); };
const enforcerTools = await enforcerMod.OmtEnforcer({ client: null, $: dollarStub, directory: REPO_ROOT });

const hook = enforcerTools['tool.execute.after'];

// Test 6 - MVC++ gate
const srcFile = join(REPO_ROOT, 'src', 'test_mvc_gate.py');
await fs.writeFile(srcFile, "print('ok')\n");

const sessionId = 'test-mvc-debug';

const badEditInput = {
  tool: 'edit',
  sessionID: sessionId,
  args: {
    filePath: srcFile,
    oldString: "print('ok')\n",
    newString: "import nonexistent_module\nprint('ok')\n",
  },
};
const badEditOutput = { title: 'Edit', output: 'edited', metadata: {} };

console.log('Before bad edit, output:', badEditOutput.output);
try {
  await hook(badEditInput, badEditOutput);
  console.log('After bad edit, output:', badEditOutput.output);
  console.log('No throw!');
} catch(e) {
  console.log('Threw:', e.name, e.message);
}

// Cleanup
await fs.rm(srcFile);