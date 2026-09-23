import type { FeatureManifest } from "@argus/ui";

// Pre-registered slot (M00). Owner: M05 (slot). Edit freely inside src/features/site-intel/ and src/app/site-intel/.
export const manifest: FeatureManifest = {
  id: "site-intel",
  href: "/site-intel",
  owner: "M05 (slot)",
  order: 90,
  label: { en: { label: "Site Intelligence" }, hi: { label: "साइट इंटेलिजेंस" }, ta: { label: "தள நுண்ணறிவு" } },
};
