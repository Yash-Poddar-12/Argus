import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M08 (slot). Edit freely inside src/features/training-admin/ and src/app/training-admin/.
export const manifest: FeatureManifest = {
  id: "training-admin",
  href: "/training-admin",
  owner: "M08 (slot)",
  order: 110,
  label: { en: { label: "Training Admin" }, hi: { label: "प्रशिक्षण प्रबंधन" }, ta: { label: "பயிற்சி நிர்வாகம்" } },
};
