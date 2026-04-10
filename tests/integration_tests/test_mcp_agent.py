import os

import pytest

pytestmark = pytest.mark.anyio


@pytest.mark.skipif(
    not os.getenv("MCP_SERVER_URL") and not os.getenv("MCP_SERVERS"),
    reason="MCP server not configured",
)
async def test_mcp_agent_greeting():
    from agent.mcp_agent import graph

    prompt = "请使用工具 say_hello 向名为 'pytest' 的用户打招呼，并返回结果。"
    res = await graph.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    content = res["messages"][-1].content
    assert "pytest" in content or "你好" in content
