"use client";

// Machine views for both roles.
// Placeholder views: replace each with the real feature. Keep feature-specific components in this folder.
import { SlotPlaceholder } from "@/components/ui";
import { useT, type Dict } from "@/lib/i18n";

const myMachineLabels: Dict<"title"> = { en: { title: "My Machine" }, hi: { title: "मेरी मशीन" }, ta: { title: "என் இயந்திரம்" } };

export function MyMachine() {
  const t = useT(myMachineLabels);
  return <SlotPlaceholder title={t("title")} owner="features/machines" description="Live machine state, alerts, location." />;
}

const machinesAdminLabels: Dict<"title"> = { en: { title: "Machines" }, hi: { title: "मशीनें" }, ta: { title: "இயந்திரங்கள்" } };

export function MachinesAdmin() {
  const t = useT(machinesAdminLabels);
  return <SlotPlaceholder title={t("title")} owner="features/machines" description="Machine CRUD." />;
}
