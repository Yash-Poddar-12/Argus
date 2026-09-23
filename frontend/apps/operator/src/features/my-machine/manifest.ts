import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M02. Edit freely inside src/features/my-machine/ and src/app/my-machine/.
export const manifest: FeatureManifest = {
  id: "my-machine",
  href: "/my-machine",
  owner: "M02",
  order: 20,
  label: { en: { label: "My Machine" }, hi: { label: "मेरी मशीन" }, ta: { label: "என் இயந்திரம்" } },
};
