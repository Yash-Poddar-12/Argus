import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/sites/ and src/app/sites/.
export const manifest: FeatureManifest = {
  id: "sites",
  href: "/sites",
  owner: "M03",
  order: 40,
  label: { en: { label: "Sites & Zones" }, hi: { label: "साइट और ज़ोन" }, ta: { label: "தளங்கள் & மண்டலங்கள்" } },
};
