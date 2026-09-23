"use client";

import { SlotPlaceholder, useT } from "@argus/ui";
import { manifest } from "./manifest";

// Placeholder until M02 builds this feature (see the owning module's SPEC in docs/03-modules).
export function Feature() {
  const t = useT(manifest.label);
  return <SlotPlaceholder title={t("label")} owner={manifest.owner} description="Task lifecycle, progress, live ETA and WHY? drawer." />;
}
