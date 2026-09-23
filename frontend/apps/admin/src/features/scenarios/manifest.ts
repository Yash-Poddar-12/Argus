import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M09 (slot). Edit freely inside src/features/scenarios/ and src/app/scenarios/.
export const manifest: FeatureManifest = {
  id: "scenarios",
  href: "/scenarios",
  owner: "M09 (slot)",
  order: 100,
  label: { en: { label: "What-if Scenarios" }, hi: { label: "क्या-होगा परिदृश्य" }, ta: { label: "என்ன-என்றால்" } },
};
