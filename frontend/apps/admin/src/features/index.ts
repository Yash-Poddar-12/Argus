// Pre-registered feature slots (M00). Adding a NEW slot = one line here, via a PR reviewed by the app owner.
import type { FeatureManifest } from "@argus/ui";
import { manifest as overview } from "./overview/manifest";
import { manifest as operators } from "./operators/manifest";
import { manifest as machines } from "./machines/manifest";
import { manifest as sites } from "./sites/manifest";
import { manifest as tasks } from "./tasks/manifest";
import { manifest as assignments } from "./assignments/manifest";
import { manifest as siteMap } from "./site-map/manifest";
import { manifest as safety } from "./safety/manifest";
import { manifest as siteIntel } from "./site-intel/manifest";
import { manifest as scenarios } from "./scenarios/manifest";
import { manifest as trainingAdmin } from "./training-admin/manifest";
import { manifest as analytics } from "./analytics/manifest";

export const FEATURES: FeatureManifest[] = [overview, operators, machines, sites, tasks, assignments, siteMap, safety, siteIntel, scenarios, trainingAdmin, analytics];
