import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/safety/ and src/app/safety/.
export const manifest: FeatureManifest = {
  id: "safety",
  href: "/safety",
  owner: "M03",
  order: 80,
  label: { en: { label: "Safety & Hazards" }, hi: { label: "सुरक्षा" }, ta: { label: "பாதுகாப்பு" } },
};
