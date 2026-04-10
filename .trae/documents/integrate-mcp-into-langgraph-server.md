Integrate MCP Tools Into LangGraph Dev Server

Summary
- Expose an MCP‑powered agent as a LangGraph server graph for local/dev use.
- Refactor the existing MCP client script into a proper graph export and wire it in langgraph.json.
- Keep the current agent intact and add a separate graph id for the MCP variant.

Current State Analysis
- Runtime
  - LangGraph server configured via [langgraph.json](file:///d:/Project/bigModel/langgraph_demo/langgraph.json) with a single graph id “agent” → [my_agent.py:graph](file:///d:/Project/bigModel/langgraph_demo/src/agent/my_agent.py#L28-L36).
  - my_agent.py performs import‑time invocation/prints, which is unsafe for server imports: see [my_agent.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/my_agent.py#L48-L55).
- MCP client examples
  - Async MCP integration demo exists in [mcp_agent.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/mcp_agent.py) and a token variant in [mcp_agent2.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/mcp_agent2.py), but neither exports a “graph” for the LangGraph server, and both include hardcoded endpoints and print side effects.
- MCP servers (for local testing)
  - Example servers in [tools_server.py](file:///d:/Project/bigModel/langgraph_demo/src/mcp_server/tools_server.py) and [tools_server2.py](file:///d:/Project/bigModel/langgraph_demo/src/mcp_server/tools_server2.py) expose tools like zhipuai_search and say_hello.
- Config
  - Environment handling via [env_utils.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/env_utils.py). No MCP‑specific envs yet.

Proposed Changes
1) Create MCP Graph Export
   - File: [src/agent/mcp_agent.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/mcp_agent.py)
   - What:
     - Replace the top‑level “agent = asyncio.run(create_agent())” with “graph = asyncio.run(create_graph())” and remove all print/diagnostic side effects.
     - Generalize server configuration to read from env:
       - MCP_SERVER_URL (e.g., http://127.0.0.1:8080/sse)
       - MCP_TRANSPORT (sse | streamable_http), default “sse”
       - MCP_AUTH_TOKEN (optional Bearer token for protected servers)
       - Optionally allow multiple servers via a comma‑separated MCP_SERVERS list of name=url|transport pairs; if unset, fall back to MCP_SERVER_URL.
     - Build MultiServerMCPClient from available envs, await get_tools(), and pass tools into create_react_agent.
     - Keep the existing llm selection from [my_llm.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/my_llm.py).
   - Why:
     - Provide a synchronous “graph” export compatible with the LangGraph dev server and configurable without code edits.
   - How:
     - Define async create_graph() that resolves MCP tools and returns create_react_agent(...).
     - Assign module‑level graph via asyncio.run(create_graph()).

2) Register MCP Graph in Server Config
   - File: [langgraph.json](file:///d:/Project/bigModel/langgraph_demo/langgraph.json)
   - What:
     - Add a new entry under “graphs”: "mcp_agent": "./src/agent/mcp_agent.py:graph".
   - Why:
     - Allow switching between the existing “agent” and the new MCP‑powered agent via the dev server.

3) Guard Import‑Time Side Effects in my_agent.py (stability)
   - File: [src/agent/my_agent.py](file:///d:/Project/bigModel/langgraph_demo/src/agent/my_agent.py)
   - What:
     - Move the sample invoke/prints behind if __name__ == "__main__": to avoid side effects during server import.
   - Why:
     - Prevent unintended execution when the server loads the module.

4) Optional Test (skipped by default without MCP server)
   - File: tests/integration_tests/test_mcp_agent.py
   - What:
     - Add an integration test that:
       - Skips unless MCP_SERVER_URL is set.
       - Invokes the graph via the LangGraph SDK (or direct Pregel .ainvoke) to call say_hello and asserts the tool output contains the username.
   - Why:
     - Provide a reproducible validation path without making CI flaky if no MCP server is running.

Assumptions & Decisions
- Dev server: Use the LangGraph dev server (langgraph.json) as the primary runtime.
- MCP transport: Default to SSE; allow override via MCP_TRANSPORT.
- Auth: Support optional Bearer auth header via MCP_AUTH_TOKEN for servers like tools_server2.py.
- Startup behavior: It is acceptable to resolve MCP tools at import time for dev usage; on failure, raise a clear ImportError with guidance rather than silently disabling tools.
- Backward compatibility: Keep existing “agent” graph unchanged; add a new “mcp_agent” graph id.

Verification
- Local manual validation
  - Start an MCP server locally, for example:
    - Python SSE server on :8080 from [tools_server.py](file:///d:/Project/bigModel/langgraph_demo/src/mcp_server/tools_server.py) or protected variant in [tools_server2.py](file:///d:/Project/bigModel/langgraph_demo/src/mcp_server/tools_server2.py).
  - Set env (in .env):
    - MCP_SERVER_URL=http://127.0.0.1:8080/sse
    - MCP_TRANSPORT=sse
    - MCP_AUTH_TOKEN=<optional token for protected server>
  - Start LangGraph dev server and select graph “mcp_agent”.
  - Invoke with a prompt that triggers a tool (e.g., ask for a greeting). Confirm a tool call executes and the final message includes tool output.
- Test validation (optional)
  - Run pytest with MCP_SERVER_URL set and verify tests/integration_tests/test_mcp_agent.py passes.

Out of Scope
- Production deployment or containerization.
- Advanced error handling/retry strategies for MCP connections.
- Expanding MCP tool catalogs beyond the server(s) specified by env.

Implementation Order
1) Refactor src/agent/mcp_agent.py to export “graph” and read env config.
2) Update langgraph.json with “mcp_agent” mapping.
3) Guard sample invoke in my_agent.py with __main__.
4) Add optional integration test and README snippet (if requested).
