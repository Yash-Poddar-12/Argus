import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/machines/ and src/app/machines/.
export const manifest: FeatureManifest = {
  id: "machines",
  href: "/machines",
  owner: "M03",
  order: 30,
  label: { en: { label: "Machines" }, hi: { label: "मशीनें" }, ta: { label: "இயந்திரங்கள்" } },
};
