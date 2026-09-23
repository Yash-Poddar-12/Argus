"use client";

import { useEffect, useRef, useState } from "react";
import { API_URL, session } from "./client";

/** WS message envelope pushed by the backend gateway (docs/02-contracts/API_CATALOG.md). */
export type WsMessage<T = unknown> = { type: string; version: string; timestamp: string; channel: string; data: T };
export type WsStatus = "connecting" | "open" | "closed" | "denied";

/**
 * Subscribe to a channel such as `operators/OP1001`, `machines/EXC001` or `sites/SITE_A`.
 * Reconnects with backoff; `status` drives the offline/reconnecting banner.
 */
export function useChannel(channel: string | null, onMessage: (msg: WsMessage) => void): WsStatus {
  const [status, setStatus] = useState<WsStatus>("connecting");
  const handler = useRef(onMessage);
  handler.current = onMessage;

  useEffect(() => {
    if (!channel) return;
    let ws: WebSocket | null = null;
    let attempt = 0;
    let stopped = false;
    let timer: ReturnType<typeof setTimeout> | undefined;

    const connect = () => {
      const token = session.token();
      if (!token) { setStatus("denied"); return; }
      setStatus("connecting");
      ws = new WebSocket(`${API_URL.replace(/^http/, "ws")}/ws/${channel}?token=${encodeURIComponent(token)}`);
      ws.onopen = () => { attempt = 0; setStatus("open"); };
      ws.onmessage = (e) => {
        try { handler.current(JSON.parse(e.data) as WsMessage); } catch {}
      };
      ws.onclose = (e) => {
        if (stopped) return;
        if (e.code === 4401 || e.code === 4403) { setStatus("denied"); return; }
        setStatus("closed");
        timer = setTimeout(connect, Math.min(15000, 500 * 2 ** attempt++));
      };
    };
    connect();
    return () => { stopped = true; clearTimeout(timer); ws?.close(); };
  }, [channel]);

  return status;
}
