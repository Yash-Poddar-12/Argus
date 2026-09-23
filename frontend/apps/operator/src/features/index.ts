// Pre-registered feature slots (M00). Adding a NEW slot = one line here, via a PR reviewed by the app owner.
import type { FeatureManifest } from "@argus/ui";
import { manifest as myDay } from "./my-day/manifest";
import { manifest as myMachine } from "./my-machine/manifest";
import { manifest as myTasks } from "./my-tasks/manifest";
import { manifest as mySafety } from "./my-safety/manifest";
import { manifest as myPerformance } from "./my-performance/manifest";
import { manifest as training } from "./training/manifest";
import { manifest as copilot } from "./copilot/manifest";

export const FEATURES: FeatureManifest[] = [myDay, myMachine, myTasks, mySafety, myPerformance, training, copilot];
