"use client";

// Operator home views (My Day, My Performance).
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const myDayLabels: Dict<"title"> = { en: { title: "My Day" }, hi: { title: "मेरा दिन" }, ta: { title: "என் நாள்" } };

export function MyDay() {
  const t = useT(myDayLabels);
  return <SlotPlaceholder title={t("title")} owner="features/operator" description="Shift briefing, task sequence, ETAs, conditions, what changed." />;
}

const myPerformanceLabels: Dict<"title"> = { en: { title: "My Performance" }, hi: { title: "मेरा प्रदर्शन" }, ta: { title: "என் செயல்திறன்" } };

export function MyPerformance() {
  const t = useT(myPerformanceLabels);
  return <SlotPlaceholder title={t("title")} owner="features/operator" description="Non-punitive trends, baselines and context." />;
}
