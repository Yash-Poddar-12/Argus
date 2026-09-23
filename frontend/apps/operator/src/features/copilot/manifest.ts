import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M07 (slot). Edit freely inside src/features/copilot/ and src/app/copilot/.
export const manifest: FeatureManifest = {
  id: "copilot",
  href: "/copilot",
  owner: "M07 (slot)",
  order: 70,
  label: { en: { label: "AI Copilot" }, hi: { label: "एआई सहायक" }, ta: { label: "AI உதவியாளர்" } },
};
