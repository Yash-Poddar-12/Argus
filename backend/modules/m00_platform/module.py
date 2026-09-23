"""M00 platform module: discovered automatically by backend/core/registry.py."""

from backend.modules.m00_platform.api import router

MODULE_ID = "M00"
event_handlers: list = []
ws_message_types: list[str] = []
permissions: dict[str, list[str]] = {}

__all__ = ["MODULE_ID", "router", "event_handlers", "ws_message_types", "permissions"]
