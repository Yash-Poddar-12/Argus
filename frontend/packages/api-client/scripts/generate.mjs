// Generates TypeScript types from contracts/openapi/*.yaml into src/generated/ (M00).
// Never hand-edit src/generated. CI fails if the output drifts from the contracts.
import openapiTS, { astToString } from "openapi-typescript";
import { readdirSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const contracts = resolve(here, "../../../../contracts/openapi");
const out = resolve(here, "../src/generated");
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

const names = [];
for (const file of readdirSync(contracts).filter((f) => f.endsWith(".yaml")).sort()) {
  const name = file.replace(/\.yaml$/, "");
  const ast = await openapiTS(pathToFileURL(join(contracts, file)));
  const header = `// GENERATED from contracts/openapi/${file} by packages/api-client/scripts/generate.mjs. Do not edit.\n`;
  writeFileSync(join(out, `${name}.ts`), header + astToString(ast));
  names.push(name);
}
const ident = (n) => n.replace(/-([a-z0-9])/g, (_, c) => c.toUpperCase());
writeFileSync(
  join(out, "index.ts"),
  "// GENERATED. Do not edit.\n" + names.map((n) => `export type * as ${ident(n)} from "./${n}";`).join("\n") + "\n",
);
console.log(`generated ${names.length} module type file(s) -> src/generated`);
