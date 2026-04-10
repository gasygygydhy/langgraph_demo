from langgraph.prebuilt.chat_agent_executor import AgentState


#  自己定义的智能体的状态 类
class CustomState1(AgentState):
    username: str # 用户名