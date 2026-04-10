import os
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

from agent.my_llm import llm


def _build_mcp_client_from_env() -> MultiServerMCPClient:
    token = os.getenv("MCP_AUTH_TOKEN")
    transport_default = os.getenv("MCP_TRANSPORT", "sse")
    servers_env = os.getenv("MCP_SERVERS")
    server_url = os.getenv("MCP_SERVER_URL")

    servers: dict[str, dict] = {}
    headers = {"Authorization": f"Bearer {token}"} if token else None

    if servers_env:
        # Format: name=url|transport,name2=url2|transport2
        for item in [s.strip() for s in servers_env.split(",") if s.strip()]:
            name, rest = item.split("=", 1)
            if "|" in rest:
                url, transport = rest.split("|", 1)
            else:
                url, transport = rest, transport_default
            cfg = {"url": url.strip(), "transport": transport.strip()}
            if headers:
                cfg["headers"] = headers
            servers[name.strip()] = cfg
    elif server_url:
        cfg = {"url": server_url.strip(), "transport": transport_default}
        if headers:
            cfg["headers"] = headers
        servers["default_mcp"] = cfg
    else:
        raise ImportError(
            "MCP server not configured. Set MCP_SERVER_URL (and MCP_TRANSPORT), "
            "or MCP_SERVERS (e.g., name=http://127.0.0.1:8080/sse|sse)."
        )

    return MultiServerMCPClient(servers)


async def create_graph():
    mcp_client = _build_mcp_client_from_env()
    mcp_tools = await mcp_client.get_tools()
    return create_react_agent(
        llm,
        tools=mcp_tools,
        prompt="你是一个智能助手，尽可能的调用工具回答用户的问题",
    )


graph = asyncio.run(create_graph())

