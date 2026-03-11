"""Istedlal MCP Server - Entry point."""
from starlette.responses import JSONResponse, Response

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import AnyHttpUrl

from src.auth import StaticBearerTokenVerifier
from src.config import config
from src.tools import register_tools

# Transport security: allow all hosts, rely on Bearer token for auth
# (disable DNS rebinding protection so no "Invalid Host header" in production)
_transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Bearer token auth (optional) - when MCP_BEARER_TOKEN is set, /mcp requires Authorization: Bearer <token>
# Multiple tokens supported: MCP_BEARER_TOKEN=token1,token2,token3
_auth: AuthSettings | None = None
_token_verifier: StaticBearerTokenVerifier | None = None
_tokens = [t.strip() for t in config.MCP_BEARER_TOKEN.split(",") if t.strip()]
if _tokens:
    _auth = AuthSettings(
        issuer_url=AnyHttpUrl("https://localhost/issuer"),
        resource_server_url=AnyHttpUrl(config.MCP_RESOURCE_SERVER_URL),
        required_scopes=["mcp"],
    )
    _token_verifier = StaticBearerTokenVerifier(_tokens)

mcp = FastMCP(
    "Istedlal MCP Server",
    json_response=True,
    stateless_http=True,  # No session ID needed - works better with MCP Inspector / proxy
    transport_security=_transport_security,
    auth=_auth,
    token_verifier=_token_verifier,
)

# Register all tools
register_tools(mcp)


@mcp.custom_route("/", methods=["GET"])
async def root_info(request):
    """Simple info page at root - avoid 404 when visiting http://localhost:8000/"""
    return JSONResponse({
        "name": "Istedlal MCP Server",
        "status": "running",
        "mcp_endpoint": "/mcp",
        "message": "Connect to /mcp for MCP protocol (MCP Inspector, Cursor, etc.)",
        "tools": ["get_file_metadata", "search_files", "semantic_search_files"],
    })


@mcp.custom_route("/favicon.ico", methods=["GET"])
async def favicon(request):
    """Avoid 404 for favicon requests from browser."""
    return Response(status_code=204)


def run() -> None:
    """Start the MCP server with configured transport."""
    if config.MCP_TRANSPORT == "streamable-http":
        import anyio
        import uvicorn
        from starlette.middleware.cors import CORSMiddleware

        app = mcp.streamable_http_app()
        # CORS for MCP Inspector Direct mode (browser at localhost:6274 → localhost:8000)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        async def _serve():
            config_uv = uvicorn.Config(
                app,
                host=config.HTTP_HOST,
                port=config.HTTP_PORT,
                log_level=config.LOG_LEVEL.lower(),
            )
            server = uvicorn.Server(config_uv)
            await server.serve()

        anyio.run(_serve)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    run()
