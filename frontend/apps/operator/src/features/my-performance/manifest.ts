import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M02. Edit freely inside src/features/my-performance/ and src/app/my-performance/.
export const manifest: FeatureManifest = {
  id: "my-performance",
  href: "/my-performance",
  owner: "M02",
  order: 50,
  label: { en: { label: "My Performance" }, hi: { label: "मेरा प्रदर्शन" }, ta: { label: "என் செயல்திறன்" } },
};
