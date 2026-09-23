import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M11 (slot). Edit freely inside src/features/analytics/ and src/app/analytics/.
export const manifest: FeatureManifest = {
  id: "analytics",
  href: "/analytics",
  owner: "M11 (slot)",
  order: 120,
  label: { en: { label: "Analytics" }, hi: { label: "विश्लेषण" }, ta: { label: "பகுப்பாய்வு" } },
};
