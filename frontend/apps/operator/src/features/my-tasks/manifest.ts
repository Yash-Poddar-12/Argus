import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M02. Edit freely inside src/features/my-tasks/ and src/app/my-tasks/.
export const manifest: FeatureManifest = {
  id: "my-tasks",
  href: "/my-tasks",
  owner: "M02",
  order: 30,
  label: { en: { label: "My Tasks" }, hi: { label: "मेरे कार्य" }, ta: { label: "என் பணிகள்" } },
};
