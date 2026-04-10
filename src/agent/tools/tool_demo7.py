from typing import Any, Type

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI
from agent.my_llm import llm

from agent.env_utils import ZHIPU_API_KEY

zhipuai_client = ZhipuAI(api_key=ZHIPU_API_KEY)


class SearchArgs(BaseModel):
    query: str = Field(description="需要进行网络搜索的信息。")


# 网络搜索的工具
class MySearchTool(BaseTool):
    # 工具名字
    name: str = "search_tool"

    description: str = '搜索互联网上公开内容的工具'

    return_direct: bool = False

    args_schema: Type[BaseModel] = SearchArgs

    def _run(self, query) -> str:
        try:
            # print("执行我的Python中的工具，输入的参数为:", query)
            response = zhipuai_client.web_search.web_search(
                search_engine="search_pro",
                search_query=query
            )
            # print(response)
            if response.search_result:
                return "\n\n".join([d.content for d in response.search_result])
            return '没有搜索到任何内容！'
        except Exception as e:
            print(e)
            return '没有搜索到任何内容！'



# my_tool = MySearchTool()
# print(my_tool.name)
# print(my_tool.description)
# print(my_tool.args_schema.model_json_schema())