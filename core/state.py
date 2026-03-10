from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    全局状态字典，相当于整个微型公司的“共享白板”。
    """
    # 消息历史：使用 add_messages 自动把新消息追加到列表末尾
    messages: Annotated[Sequence[BaseMessage], add_messages]
      
    # 记录当前应该由哪个 Agent 执行任务
    next_node: str
