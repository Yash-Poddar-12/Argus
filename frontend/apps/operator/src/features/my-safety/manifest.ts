import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M02. Edit freely inside src/features/my-safety/ and src/app/my-safety/.
export const manifest: FeatureManifest = {
  id: "my-safety",
  href: "/my-safety",
  owner: "M02",
  order: 40,
  label: { en: { label: "My Safety" }, hi: { label: "मेरी सुरक्षा" }, ta: { label: "என் பாதுகாப்பு" } },
};
