from typing_extensions import TypedDict
from langchain.agents import AgentState


#  自己定义的智能体的状态 类
class CustomState(AgentState, TypedDict):
    username: str # 用户名



