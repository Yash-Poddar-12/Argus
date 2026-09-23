"use client";

// Safety views: operator safety and supervisor hazards/rules.
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const mySafetyLabels: Dict<"title"> = { en: { title: "My Safety" }, hi: { title: "मेरी सुरक्षा" }, ta: { title: "என் பாதுகாப்பு" } };

export function MySafety() {
  const t = useT(mySafetyLabels);
  return <SlotPlaceholder title={t("title")} owner="features/safety" description="Safety status, recent events, hazards, why an alert fired." />;
}

const safetyAdminLabels: Dict<"title"> = { en: { title: "Safety & Hazards" }, hi: { title: "सुरक्षा" }, ta: { title: "பாதுகாப்பு" } };

export function SafetyAdmin() {
  const t = useT(safetyAdminLabels);
  return <SlotPlaceholder title={t("title")} owner="features/safety" description="Live hazards, rules/thresholds, device registry." />;
}
