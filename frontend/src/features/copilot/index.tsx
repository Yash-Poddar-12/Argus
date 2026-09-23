"use client";

// Operator Copilot (voice + text), grounded in backend tool results.
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const copilotLabels: Dict<"title"> = { en: { title: "AI Copilot" }, hi: { title: "एआई सहायक" }, ta: { title: "AI உதவியாளர்" } };

export function Copilot() {
  const t = useT(copilotLabels);
  return <SlotPlaceholder title={t("title")} owner="features/copilot" description="Voice and text copilot grounded in tool results." />;
}
