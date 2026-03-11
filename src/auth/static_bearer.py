"""Static Bearer token verifier for MCP server."""
import hmac

from mcp.server.auth.provider import AccessToken, TokenVerifier


def _secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison."""
    return hmac.compare_digest(a.encode(), b.encode())


class StaticBearerTokenVerifier(TokenVerifier):
    """Verifies Bearer token against one or more configured secrets (constant-time)."""

    def __init__(self, expected_tokens: list[str]):
        self._tokens = [t.strip() for t in expected_tokens if t and t.strip()]

    async def verify_token(self, token: str) -> AccessToken | None:
        if not token or not self._tokens:
            return None
        for expected in self._tokens:
            if _secure_compare(token, expected):
                return AccessToken(
                    token=token,
                    client_id="mcp-client",
                    scopes=["mcp"],
                    expires_at=None,
                )
        return None
