import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/overview/ and src/app/overview/.
export const manifest: FeatureManifest = {
  id: "overview",
  href: "/overview",
  owner: "M03",
  order: 10,
  label: { en: { label: "Overview" }, hi: { label: "अवलोकन" }, ta: { label: "மேலோட்டம்" } },
};
