import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/operators/ and src/app/operators/.
export const manifest: FeatureManifest = {
  id: "operators",
  href: "/operators",
  owner: "M03",
  order: 20,
  label: { en: { label: "Operators" }, hi: { label: "ऑपरेटर" }, ta: { label: "இயக்குநர்கள்" } },
};
