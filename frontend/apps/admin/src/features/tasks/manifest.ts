import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/tasks/ and src/app/tasks/.
export const manifest: FeatureManifest = {
  id: "tasks",
  href: "/tasks",
  owner: "M03",
  order: 50,
  label: { en: { label: "Tasks" }, hi: { label: "कार्य" }, ta: { label: "பணிகள்" } },
};
