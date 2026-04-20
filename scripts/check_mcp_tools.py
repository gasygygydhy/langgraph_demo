import asyncio
import os
import sys
from pathlib import Path

from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv


async def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    load_dotenv(project_root / ".env", override=True)

    url = os.getenv("MCP_SERVER_URL") or (sys.argv[1] if len(sys.argv) > 1 else None)
    transport = os.getenv("MCP_TRANSPORT", "sse")
    name_filter = os.getenv("MCP_TOOL_FILTER") or (sys.argv[2] if len(sys.argv) > 2 else "")
    if not url:
        raise SystemExit(
            "MCP_SERVER_URL is required. Configure it in project .env or as an environment variable."
        )

    client = MultiServerMCPClient({"default": {"url": url, "transport": transport}})
    tools = await client.get_tools()
    print(f"url={url}")
    print(f"transport={transport}")
    print(f"tools_count={len(tools)}")
    for t in tools:
        name = getattr(t, "name", repr(t))
        if name_filter and name_filter.lower() not in str(name).lower():
            continue
        print(name)


if __name__ == "__main__":
    asyncio.run(main())
