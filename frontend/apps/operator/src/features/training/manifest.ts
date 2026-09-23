import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M08 (slot). Edit freely inside src/features/training/ and src/app/training/.
export const manifest: FeatureManifest = {
  id: "training",
  href: "/training",
  owner: "M08 (slot)",
  order: 60,
  label: { en: { label: "My Training" }, hi: { label: "मेरा प्रशिक्षण" }, ta: { label: "என் பயிற்சி" } },
};
