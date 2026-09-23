// The only way the frontend talks to the platform: the backend REST API (+ WebSocket in lib/websocket).
// Never call databases, ML services or LLMs directly from the browser.
export * from "./client";
export type * as contracts from "./generated/argus-api";
