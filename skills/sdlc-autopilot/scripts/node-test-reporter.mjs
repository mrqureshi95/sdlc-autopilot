// Only counts named runner events, excluding Node's successful file-only wrapper.
// A repository can spoof output; this is measurement, not a tamper-proof attestation.
import { resolve } from 'node:path';
export default async function* (events) {
  let passed = 0, failed = 0;
  for await (const event of events) {
    if (!['test:pass', 'test:fail'].includes(event.type)) continue;
    const d = event.data;
    const fileWrapper = d.file && resolve(d.name) === resolve(d.file);
    if (d.skip || d.todo) continue;
    if (event.type === 'test:fail') failed++;
    else if (!fileWrapper && d.details?.type !== 'suite' && !d.skip && !d.todo) passed++;
  }
  yield `SDLC_NODE_EVIDENCE ${JSON.stringify({ passed, failed })}\n`;
}
