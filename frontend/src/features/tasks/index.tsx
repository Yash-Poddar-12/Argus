"use client";

// Task views: operator task flow and supervisor task/assignment management.
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const myTasksLabels: Dict<"title"> = { en: { title: "My Tasks" }, hi: { title: "मेरे कार्य" }, ta: { title: "என் பணிகள்" } };

export function MyTasks() {
  const t = useT(myTasksLabels);
  return <SlotPlaceholder title={t("title")} owner="features/tasks" description="Task lifecycle, progress, live ETA and WHY? drawer." />;
}

const tasksAdminLabels: Dict<"title"> = { en: { title: "Tasks" }, hi: { title: "कार्य" }, ta: { title: "பணிகள்" } };

export function TasksAdmin() {
  const t = useT(tasksAdminLabels);
  return <SlotPlaceholder title={t("title")} owner="features/tasks" description="Tasks, deadlines, targets and assistance." />;
}

const assignmentsLabels: Dict<"title"> = { en: { title: "Assignments" }, hi: { title: "असाइनमेंट" }, ta: { title: "ஒதுக்கீடுகள்" } };

export function Assignments() {
  const t = useT(assignmentsLabels);
  return <SlotPlaceholder title={t("title")} owner="features/tasks" description="Assign operator + machine + task with consequence preview." />;
}
