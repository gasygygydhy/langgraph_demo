from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState

from agent.my_llm import llm
from agent.my_state import CustomState, CustomState1
from agent.tools.tool_demo4 import calculate4
from agent.tools.tool_demo6 import runnable_tool
from agent.tools.tool_demo7 import MySearchTool
from agent.tools.tool_demo8 import get_user_info_by_name
from agent.tools.tool_demo9 import get_user_name, greet_user

# def get_weather(city: str) -> str:
#     """Get weather for a given city."""
#     return f"It's always sunny in {city}!"

# 创建一个网络搜索的工具
search_tool = MySearchTool()


# 提示词模板的函数: 由用户传入内容，组成一个动态的系统提示词
def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
    user_name = config['configurable'].get('user_name', 'zs')
    print(user_name)
    system_message = f'你是一个智能助手，尽可能的调用工具回答用户的问题，当前用户的名字是: {user_name}'
    return [{'role': 'system', 'content': system_message}] + state['messages']


graph = create_react_agent(
    llm,
    # tools=[calculate4, runnable_tool, search_tool, get_user_info_by_name],
    tools=[calculate4, runnable_tool, search_tool, get_user_name, greet_user],
    # prompt="你是一个智能助手，尽可能的调用工具回答用户的问题"
    prompt=prompt,
    state_schema=CustomState1,  # 指定自定义状态类
)

# 执行智能体，不需要严格的目录结构
# for token, metadata in graph.stream(
#     input={"messages": [{"role": "user", "content": "计算一下(3 + 5) x 12的结果"}]},
#     stream_mode='messages-tuple'
# ):
#     print("Token", token)
#     print("Metadata", metadata)
#     print("\n")


res = graph.invoke(
    {"messages": [{"role": "user", "content": "给我一个小品的报幕词"}]},
    config={"configurable": {"user_name": "laoxiao"}},
)
#
print(res['messages'][-1].content)