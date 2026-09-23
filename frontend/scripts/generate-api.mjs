// Generates TypeScript types from contracts/openapi/argus-api.yaml into src/lib/api/generated/.
// Never hand-edit src/lib/api/generated. CI fails if the output drifts from the contract.
import openapiTS, { astToString } from "openapi-typescript";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const spec = resolve(here, "../../contracts/openapi/argus-api.yaml");
const out = resolve(here, "../src/lib/api/generated");
mkdirSync(out, { recursive: true });
const ast = await openapiTS(pathToFileURL(spec));
writeFileSync(
  resolve(out, "argus-api.ts"),
  "// GENERATED from contracts/openapi/argus-api.yaml by scripts/generate-api.mjs. Do not edit.\n" + astToString(ast),
);
console.log("generated src/lib/api/generated/argus-api.ts");
