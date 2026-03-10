from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage
from core.state import AgentState
from agents.supervisor import supervisor_node
from agents.researcher import researcher_node
from agents.file_manager import file_manager_node
import os
from langgraph.checkpoint.memory import MemorySaver # 引入内存记忆（商用可换成 Postgres）

def build_graph():
    # 1. 初始化状态机图
    workflow = StateGraph(AgentState)
    print(f'main workflow-------------{workflow}')
    # 初始化记忆存储器
    memory = MemorySaver()
    # 2. 添加所有节点 (员工)
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("file_manager", file_manager_node)
    
    # 3. 定义图的连线逻辑
    # 程序一启动，先交给 supervisor
    workflow.add_edge(START, "supervisor")
    
    # 定义路由条件函数
    def router(state: AgentState):
        if state["next_node"] == "FINISH":
            return END
        return state["next_node"]
    
    # supervisor 节点结束后，根据其内部状态中的 next_node 进行条件跳转
    workflow.add_conditional_edges("supervisor", router)
    
    # 子 Agent 干完活后，必须强制把结果交回给 supervisor 进行验收或分配下一步
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("file_manager", "supervisor")
    
    # 4. 编译图，生成可执行程序
    return workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # 编译 Agent
    app = build_graph()
    print("=== 通用 Agent 已启动 ===")
    
    # 必须要给当前的对话分配一个“线程 ID”，Agent 靠这个认出你
    config = {"configurable": {"thread_id": "my_first_general_agent"}}
    print(f'main config-------------{config}')
    # 设定用户任务
    user_query = "帮我搜一下最新的mtn进展，并把搜到的一篇长新闻彻底读一遍总结下来。"
    initial_state = {"messages": [HumanMessage(content=user_query)], "next_node": ""}
    print(f'main initial_state -------------{initial_state }')
    print(f"\nUser: {user_query}\n")
    
    # 初始化状态并运行
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "next_node": "" # 初始为空
    }
    
    print(f'main initial_state -------------{initial_state }')

    # 以流式方式输出图的运行过程，方便你观察底层的 Function Call
    for step in app.stream(initial_state, config=config, stream_mode="updates"):
        for node_name, state_update in step.items():
            print(f"\n--- 节点结束: {node_name} ---")
            if "messages" in state_update and state_update["messages"]:
                 # 打印最新产生的消息
                 print(f"产出信息: {state_update['messages'][-1].content}")

    print("\n=== 任务流转结束 ===")


# LangGraph + Supervisor + 子节点 + Function Call 搭建的这套系统，在当前的 AI 工业界有几个标准的专业术语：

# Agentic Workflow（智能体工作流）

# 这是由 AI 巨头吴恩达（Andrew Ng）今年大力倡导的核心概念。它强调不要指望大模型一次性“端到端”给出完美答案，而是通过**反思（Reflection）、工具使用（Tool Use）、规划（Planning）和多智能体协作（Multi-agent Collaboration）**的“工作流”来完成复杂任务。你写的正是一个标准的智能体工作流。

# Routing Multi-Agent System（路由型多智能体系统 / 监督者架构）

# 因为你有一个不干具体活、只负责分发任务的 Supervisor，这在架构模式上被称为 Supervisor-Worker Pattern（主管-员工模式） 或 Routing MAS。

# Stateful Agent（状态化智能体）

# 传统大模型是无状态的（一问一答就忘了）。因为你引入了 LangGraph 的 AgentState 和 Checkpointer，你的系统拥有了全局记忆和进度追踪能力，这就是“状态化”。

# 用一句最装逼但也最准确的话向别人介绍你的项目：

# “我基于 LangGraph 搭建了一个支持底层 Function Calling 的路由型多智能体工作流 (Routing MAS)，并实现了状态持久化。”
