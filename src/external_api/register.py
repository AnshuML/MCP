"""Register external API endpoints as MCP tools from config."""
import inspect
import logging
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from .client import call_api
from .loader import load_config

logger = logging.getLogger(__name__)


def _make_tool_handler(
    base_url: str,
    path: str,
    method: str,
    auth: str,
    auth_env: str | None,
    timeout_sec: int,
    param_names: list[str],
    description: str,
) -> Callable[..., dict[str, Any]]:
    """Build a callable that FastMCP can introspect (signature with param names)."""

    def handler(**kwargs: Any) -> dict[str, Any]:
        params = {k: v for k, v in kwargs.items() if k in param_names and v is not None}
        return call_api(
            base_url=base_url,
            path=path,
            method=method,
            params=params,
            auth=auth,
            auth_env=auth_env,
            timeout_sec=timeout_sec,
        )

    handler.__doc__ = description or f"Call {method} {path}"
    handler.__signature__ = inspect.Signature(
        [
            inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, default=None, annotation=str)
            for name in param_names
        ]
    )
    return handler


def register_external_api_tools(mcp: FastMCP) -> None:
    """
    Load config/apis.yaml and register one MCP tool per endpoint.
    No code change needed to add APIs - only config + env.
    """
    apis = load_config()
    for api in apis:
        api_id = api.get("id") or "unknown"
        base_url = api.get("base_url", "")
        auth = (api.get("auth") or "none").strip().lower()
        auth_env = (api.get("auth_env") or "").strip() or None
        timeout_sec = int(api.get("timeout_sec") or 30)
        endpoints = api.get("endpoints") or []
        for ep in endpoints:
            if not isinstance(ep, dict):
                continue
            tool_name = (ep.get("tool_name") or "").strip()
            path = (ep.get("path") or "").strip()
            method = (ep.get("method") or "GET").upper()
            description = (ep.get("description") or f"{method} {path}").strip()
            param_names = ep.get("params") or []
            if not tool_name or not path:
                logger.warning("Endpoint missing tool_name or path: %s", ep)
                continue
            handler = _make_tool_handler(
                base_url=base_url,
                path=path,
                method=method,
                auth=auth,
                auth_env=auth_env,
                timeout_sec=timeout_sec,
                param_names=param_names,
                description=description,
            )
            mcp.tool(name=tool_name)(handler)
            logger.info("Registered tool: %s (%s %s)", tool_name, method, path)
