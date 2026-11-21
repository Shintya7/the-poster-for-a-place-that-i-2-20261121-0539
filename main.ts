import { copyFileSync, mkdirSync, readFileSync, statSync, chmodSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

const MAX_BYTES = 1048576;
const MAX_DIM = 1024;
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const here = dirname(resolve(process.argv[1]));
const source = join(here, "entry.png");
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? "/output");
const target = join(outDir, "entry.png");

const stat = statSync(source);
if (stat.size > MAX_BYTES) {
  throw new Error(`entry_too_large: entry.png is ${stat.size} bytes, over ${MAX_BYTES}`);
}

const bytes = readFileSync(source);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry_not_png: entry.png does not start with the PNG magic bytes");
}
if (bytes.length < 33 || bytes.toString("ascii", 12, 16) !== "IHDR") {
  throw new Error("entry_no_ihdr: entry.png has no IHDR chunk where one is expected");
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > MAX_DIM || height > MAX_DIM) {
  throw new Error(`entry_too_large: entry.png is ${width}x${height}, over ${MAX_DIM}x${MAX_DIM}`);
}

mkdirSync(outDir, { recursive: true, mode: 0o755 });
copyFileSync(source, target);
chmodSync(target, 0o644);
console.log(`Validated OK and copied entry.png (${width}x${height}, ${stat.size} bytes) to ${target}`);
