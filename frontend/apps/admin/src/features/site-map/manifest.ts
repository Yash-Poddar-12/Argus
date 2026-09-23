import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/site-map/ and src/app/site-map/.
export const manifest: FeatureManifest = {
  id: "site-map",
  href: "/site-map",
  owner: "M03",
  order: 70,
  label: { en: { label: "Site Map" }, hi: { label: "साइट मानचित्र" }, ta: { label: "தள வரைபடம்" } },
};
