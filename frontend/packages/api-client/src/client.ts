/** Minimal typed fetch wrapper around the platform API (M00). Types come from ./generated. */

export const API_URL = (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL) || "http://localhost:8000";
const TOKEN_KEY = "argus.token";
const PRINCIPAL_KEY = "argus.principal";

export type Principal = {
  user_id: string;
  username: string;
  role: "OPERATOR" | "SUPERVISOR_ADMIN";
  operator_id?: string | null;
  site_ids: string[];
};

export type ErrorEnvelope = { error: { code: string; message: string; details?: unknown; request_id?: string | null } };

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string, public details?: unknown) {
    super(message);
  }
}

export const session = {
  token(): string | null {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  principal(): Principal | null {
    try {
      const raw = localStorage.getItem(PRINCIPAL_KEY);
      return raw ? (JSON.parse(raw) as Principal) : null;
    } catch { return null; }
  },
  save(token: string, principal: Principal) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(PRINCIPAL_KEY, JSON.stringify(principal));
  },
  clear() {
    try { localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(PRINCIPAL_KEY); } catch {}
  },
};

export async function api<T>(path: string, init: RequestInit & { json?: unknown } = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = session.token();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  let body = init.body;
  if (init.json !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(init.json);
  }
  const res = await fetch(`${API_URL}${path}`, { ...init, headers, body });
  if (!res.ok) {
    const err = (await res.json().catch(() => null)) as ErrorEnvelope | null;
    if (res.status === 401) session.clear();
    throw new ApiError(res.status, err?.error.code ?? "HTTP_ERROR", err?.error.message ?? res.statusText, err?.error.details);
  }
  return (res.status === 204 ? undefined : await res.json()) as T;
}

export async function login(username: string, password: string): Promise<Principal> {
  const r = await api<{ access_token: string; principal: Principal }>("/api/v1/auth/login", {
    method: "POST",
    json: { username, password },
  });
  session.save(r.access_token, r.principal);
  return r.principal;
}
