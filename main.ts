// Velmara — travel poster for a place that does not exist.
// This entrypoint checks the poster image next to this script and
// hands it to the harness: it must be a whole 1024x1024 PNG under
// the 1 MiB cap, and it lands in $MAKEFUN_OUTPUT_DIR/entry.png.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1_048_576;
const SIDE = 1024;

function die(message: string): never {
  console.error(`poster: ${message}`);
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");

if (!existsSync(source)) die(`missing poster image at ${source}`);

const bytes = readFileSync(source);

if (bytes.length > MAX_BYTES) {
  die(`poster is ${bytes.length} bytes, over the ${MAX_BYTES} byte cap`);
}

const signature = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
for (let i = 0; i < signature.length; i++) {
  if (bytes[i] !== signature[i]) die("poster is not a PNG file");
}

// IHDR chunk: width lives at bytes 16..20, height at 20..24,
// both big-endian.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== SIDE || height !== SIDE) {
  die(`poster is ${width}x${height}, expected ${SIDE}x${SIDE}`);
}

const outDir = process.env.MAKEFUN_OUTPUT_DIR;
if (!outDir) die("MAKEFUN_OUTPUT_DIR is not set");

mkdirSync(outDir, { recursive: true });
const target = join(outDir, "entry.png");
writeFileSync(target, bytes);
console.log(`poster: wrote ${target} (${bytes.length} bytes, ${width}x${height})`);
