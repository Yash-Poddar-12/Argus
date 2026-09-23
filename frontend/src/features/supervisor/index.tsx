"use client";

// Supervisor/Admin console views (overview, operators, sites, site map).
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const overviewLabels: Dict<"title"> = { en: { title: "Overview" }, hi: { title: "अवलोकन" }, ta: { title: "மேலோட்டம்" } };

export function Overview() {
  const t = useT(overviewLabels);
  return <SlotPlaceholder title={t("title")} owner="features/supervisor" description="Site status at a glance and operator support context." />;
}

const operatorsLabels: Dict<"title"> = { en: { title: "Operators" }, hi: { title: "ऑपरेटर" }, ta: { title: "இயக்குநர்கள்" } };

export function Operators() {
  const t = useT(operatorsLabels);
  return <SlotPlaceholder title={t("title")} owner="features/supervisor" description="Operator CRUD." />;
}

const sitesLabels: Dict<"title"> = { en: { title: "Sites & Zones" }, hi: { title: "साइट और ज़ोन" }, ta: { title: "தளங்கள் & மண்டலங்கள்" } };

export function Sites() {
  const t = useT(sitesLabels);
  return <SlotPlaceholder title={t("title")} owner="features/supervisor" description="Site and zone CRUD, zone drawing." />;
}

const siteMapLabels: Dict<"title"> = { en: { title: "Site Map" }, hi: { title: "साइट मानचित्र" }, ta: { title: "தள வரைபடம்" } };

export function SiteMap() {
  const t = useT(siteMapLabels);
  return <SlotPlaceholder title={t("title")} owner="features/supervisor" description="Live map with togglable layers." />;
}
