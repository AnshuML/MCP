"""Generic HTTP client for external APIs. Production-grade: timeout, auth, logging."""
import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30


def call_api(
    base_url: str,
    path: str,
    method: str,
    params: dict[str, Any] | None = None,
    auth: str = "none",
    auth_env: str | None = None,
    timeout_sec: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """
    Call external API. Returns {"success": True, "data": ...} or {"success": False, "error": ...}.
    """
    url = f"{base_url.rstrip('/')}{path}" if path.startswith("/") else f"{base_url}/{path}"
    method = method.upper()
    params = params or {}

    headers = {"Content-Type": "application/json", "Accept": "application/json"}

    auth_header = None
    if auth and auth != "none" and auth_env:
        token = (__import__("os").getenv(auth_env) or "").strip()
        if token:
            if auth == "bearer":
                auth_header = ("Authorization", f"Bearer {token}")
            elif auth == "api_key":
                auth_header = ("X-API-Key", token)
        else:
            logger.warning("Auth env %s is empty for %s", auth_env, url)

    if auth_header:
        headers[auth_header[0]] = auth_header[1]

    try:
        if method == "GET":
            resp = requests.get(url, params=params, headers=headers, timeout=timeout_sec)
        elif method == "POST":
            resp = requests.post(url, json=params, headers=headers, timeout=timeout_sec)
        elif method == "PUT":
            resp = requests.put(url, json=params, headers=headers, timeout=timeout_sec)
        elif method == "DELETE":
            resp = requests.delete(url, params=params, headers=headers, timeout=timeout_sec)
        else:
            return {"success": False, "error": f"Unsupported method: {method}"}

        resp.raise_for_status()
        if resp.content:
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text[:2000]}
        else:
            data = {"status": resp.status_code}
        return {"success": True, "data": data, "status_code": resp.status_code}

    except requests.exceptions.Timeout:
        logger.exception("API timeout: %s %s", method, url)
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.RequestException as e:
        logger.exception("API request failed: %s %s - %s", method, url, e)
        err_msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                err_body = e.response.json()
                err_msg = err_body.get("detail", err_body.get("message", err_msg))
            except Exception:
                if e.response.text:
                    err_msg = e.response.text[:500]
        return {"success": False, "error": err_msg, "status_code": getattr(e.response, "status_code", None)}
    except Exception as e:
        logger.exception("Unexpected error calling API: %s", e)
        return {"success": False, "error": str(e)}
