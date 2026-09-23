"use client";

import { useMemo, useSyncExternalStore } from "react";
import { SESSION_EVENT, session, type Principal } from "@/lib/api";

const PRINCIPAL_KEY = "argus.principal";

function subscribe(onChange: () => void) {
  window.addEventListener(SESSION_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(SESSION_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

function snapshot(): string | null {
  try {
    return localStorage.getItem(PRINCIPAL_KEY);
  } catch {
    return null;
  }
}

/**
 * Current signed-in principal from the browser session.
 * Returns `undefined` during server rendering / before hydration, `null` when signed out.
 */
export function useSession(): Principal | null | undefined {
  const raw = useSyncExternalStore(subscribe, snapshot, () => undefined);
  return useMemo(() => (raw === undefined ? undefined : raw ? session.principal() : null), [raw]);
}
