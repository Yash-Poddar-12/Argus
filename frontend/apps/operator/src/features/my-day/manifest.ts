import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M02. Edit freely inside src/features/my-day/ and src/app/my-day/.
export const manifest: FeatureManifest = {
  id: "my-day",
  href: "/my-day",
  owner: "M02",
  order: 10,
  label: { en: { label: "My Day" }, hi: { label: "मेरा दिन" }, ta: { label: "என் நாள்" } },
};
