"use client";

// Training views: operator learning and supervisor training administration.
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const myTrainingLabels: Dict<"title"> = { en: { title: "My Training" }, hi: { title: "मेरा प्रशिक्षण" }, ta: { title: "என் பயிற்சி" } };

export function MyTraining() {
  const t = useT(myTrainingLabels);
  return <SlotPlaceholder title={t("title")} owner="features/training" description="Recommended modules with reasons, micro-learning, assessments, impact." />;
}

const trainingAdminLabels: Dict<"title"> = { en: { title: "Training Admin" }, hi: { title: "प्रशिक्षण प्रबंधन" }, ta: { title: "பயிற்சி நிர்வாகம்" } };

export function TrainingAdmin() {
  const t = useT(trainingAdminLabels);
  return <SlotPlaceholder title={t("title")} owner="features/training" description="Catalogue, triggers, operator training status, impact." />;
}
