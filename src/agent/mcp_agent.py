import os
import json
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from agent.my_llm import llm


MCP_DEFAULT_ENABLE = True
MCP_DEFAULT_SCHEME = "http"
MCP_DEFAULT_HOST = "127.0.0.1"
MCP_DEFAULT_PORT = "8443"
MCP_DEFAULT_PATH = "/sse"
MCP_DEFAULT_TRANSPORT = "sse"


_MCP_CLIENT: MultiServerMCPClient | None = None
_MCP_TOOLS = None
_MCP_SESSIONS: dict[str, tuple[object, object]] = {}


def _parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_args(value: str | None) -> list[str]:
    if not value:
        return []
    value = value.strip()
    if not value:
        return []
    if value.startswith("["):
        parsed = json.loads(value)
        if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
            raise ImportError("MCP_ARGS must be a JSON list of strings when using JSON format.")
        return parsed
    return [part.strip() for part in value.split(";") if part.strip()]


def _build_mcp_client_from_env() -> MultiServerMCPClient:
    token = os.getenv("MCP_AUTH_TOKEN")
    transport_default = os.getenv("MCP_TRANSPORT", MCP_DEFAULT_TRANSPORT)
    servers_env = os.getenv("MCP_SERVERS")
    server_url = os.getenv("MCP_SERVER_URL")
    enable = _parse_bool(os.getenv("MCP_ENABLE", str(MCP_DEFAULT_ENABLE)))
    command = os.getenv("MCP_COMMAND", "python").strip()
    args = _parse_args(os.getenv("MCP_ARGS"))

    servers: dict[str, dict] = {}
    headers = {"Authorization": f"Bearer {token}"} if token else None

    if servers_env:
        # Format: name=url|transport,name2=url2|transport2
        for item in [s.strip() for s in servers_env.split(",") if s.strip()]:
            try:
                name, rest = item.split("=", 1)
            except ValueError as e:
                raise ImportError(
                    "Invalid MCP_SERVERS format. Expected: "
                    "name=url|transport,name2=url2|transport2"
                ) from e
            if "|" in rest:
                url, transport = rest.split("|", 1)
            else:
                url, transport = rest, transport_default
            cfg = {"url": url.strip(), "transport": transport.strip()}
            if headers:
                cfg["headers"] = headers
            servers[name.strip()] = cfg
    elif server_url:
        if transport_default.strip().lower() == "stdio":
            raise ImportError("When MCP_TRANSPORT=stdio, configure MCP_COMMAND and MCP_ARGS instead of MCP_SERVER_URL.")
        cfg = {"url": server_url.strip(), "transport": transport_default}
        if headers:
            cfg["headers"] = headers
        servers["default_mcp"] = cfg
    elif enable:
        if transport_default.strip().lower() == "stdio":
            if not args:
                raise ImportError("When MCP_TRANSPORT=stdio, set MCP_ARGS (use ';' separated or JSON array).")
            servers["default_mcp"] = {"command": command, "args": args, "transport": "stdio"}
            return MultiServerMCPClient(servers)
        scheme = os.getenv("MCP_SCHEME", MCP_DEFAULT_SCHEME).strip()
        host = os.getenv("MCP_HOST", MCP_DEFAULT_HOST).strip()
        port = os.getenv("MCP_PORT", MCP_DEFAULT_PORT).strip()
        path = os.getenv("MCP_PATH", MCP_DEFAULT_PATH).strip()
        cfg = {"url": f"{scheme}://{host}:{port}{path}", "transport": transport_default}
        if headers:
            cfg["headers"] = headers
        servers["default_mcp"] = cfg
    else:
        raise ImportError(
            "MCP server not configured. Set MCP_SERVER_URL (and MCP_TRANSPORT), "
            "or MCP_SERVERS (e.g., name=http://127.0.0.1:8443/sse|sse). "
            "Alternatively set MCP_ENABLE=1 to use defaults (127.0.0.1:8443/sse), "
            "or set MCP_TRANSPORT=stdio with MCP_COMMAND and MCP_ARGS."
        )

    return MultiServerMCPClient(servers)


async def _get_mcp_tools():
    global _MCP_CLIENT, _MCP_TOOLS

    if _MCP_TOOLS is not None:
        return _MCP_TOOLS

    if _MCP_CLIENT is None:
        _MCP_CLIENT = _build_mcp_client_from_env()

    stateful = _parse_bool(os.getenv("MCP_STATEFUL", "0"))
    if stateful:
        servers = getattr(_MCP_CLIENT, "servers", None) or {}
        for server_name in servers.keys():
            if server_name in _MCP_SESSIONS:
                continue
            session_cm = _MCP_CLIENT.session(server_name)
            session = await session_cm.__aenter__()
            _MCP_SESSIONS[server_name] = (session_cm, session)

        tools = []
        for _, session in _MCP_SESSIONS.values():
            tools.extend(await load_mcp_tools(session))
        _MCP_TOOLS = tools
        return _MCP_TOOLS

    _MCP_TOOLS = await _MCP_CLIENT.get_tools()
    return _MCP_TOOLS


async def create_graph():
    mcp_tools = await _get_mcp_tools()
    allowlist = os.getenv("MCP_TOOL_ALLOWLIST")
    blocklist = os.getenv("MCP_TOOL_BLOCKLIST")
    if allowlist:
        allow = {name.strip() for name in allowlist.split(",") if name.strip()}
        mcp_tools = [t for t in mcp_tools if getattr(t, "name", None) in allow]
    if blocklist:
        block = {name.strip() for name in blocklist.split(",") if name.strip()}
        mcp_tools = [t for t in mcp_tools if getattr(t, "name", None) not in block]
    if not mcp_tools:
        raise ImportError("No MCP tools available after filtering; check MCP_* configuration.")
    return create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )


graph = asyncio.run(create_graph())

