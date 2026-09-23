import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M03. Edit freely inside src/features/assignments/ and src/app/assignments/.
export const manifest: FeatureManifest = {
  id: "assignments",
  href: "/assignments",
  owner: "M03",
  order: 60,
  label: { en: { label: "Assignments" }, hi: { label: "असाइनमेंट" }, ta: { label: "ஒதுக்கீடுகள்" } },
};
