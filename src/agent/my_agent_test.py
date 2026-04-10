from langchain.agents import create_agent

from mcp_server.tools_server2 import my_search
from .my_llm import llm
from .tools import tool_demo5
from .tools import tool_demo7





create_agent(
    llm,
    tools=[tool_demo5.calculater, tool_demo7.MySearchTool],
    middleware = [pr]

)


def calculate5(
        a:float,
        b:float,
        operation: str)-> float:
    """工具函数：计算两个数字的运算结果

    Args:
    a: 第一个需要输入的数字。
    b: 第二个需要输入的数字。
    operation: 运算类型，只能是add、subtract、multiply和divide中的任意一个。

    Returns:
    返回两个输入数字的运算结果。

    """
    result = 0.0
    print(a)
    print(b)
    print(operation)
    match operation:
        case "add":
            result = a + b
        case "subtract":
            result = a - b
        case "multiply":
            result = a * b
        case "divide":
            if b != 0:
                result = a / b
            else:
                raise ValueError("除数不能为零")

    return result