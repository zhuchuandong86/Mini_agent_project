import json
from langchain_core.prompts import ChatPromptTemplate
from core.llm_config import get_llm
from core.state import AgentState

def supervisor_node(state: AgentState):
    llm = get_llm()
    
    # 移除了 with_structured_output，直接在 Prompt 中强调 JSON 格式
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一个出色的项目经理 (Supervisor)。
        你手下有两个员工：
        1. researcher：擅长在互联网上搜索信息。
        2. file_manager：擅长操作本地文件系统（写入报告等）。
        
        【核心路由规则与防死循环铁律】：
        1. 仔细阅读最后一条消息！如果最后一条消息是【FileManager 工作汇报】且表明文件已保存、已处理完毕，你【必须】【立刻】返回 'FINISH'，整个项目已经大功告成！
        2. 绝不允许让同一个员工连续重复执行相同的任务！如果它刚汇报完，你绝不能再把节点路由给它！
        3. 如果任务需要查资料，交给 researcher；如果资料查完了需要保存，交给 file_manager。
        
        【强制输出格式】
        你必须且只能输出一个合法的 JSON 字符串：
        {{"next_node": "researcher" 或 "file_manager" 或 "FINISH"}}
        """),
        ("placeholder", "{messages}")
    ])
    
    chain = prompt | llm
    # 这里拿到的是一段纯文本回复
    response = chain.invoke({"messages": state["messages"]})
    
    print(f'supervisor response------------{response}')
    
    # 手动解析模型返回的纯文本 JSON
    try:
        content = response.content.strip()
        # 兼容处理：万一模型还是犯贱加了 markdown 代码块，我们帮它去掉
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        decision = json.loads(content)
        next_node = decision.get("next_node", "FINISH") # 默认安全退出
    except Exception as e:
        print(f"\n[Supervisor 解析错误] 模型没有按规定输出JSON。模型原始输出: {response.content}")
        print(f"错误信息: {str(e)}")
        next_node = "FINISH" # 遇到解析错误直接结束图，防止死循环
        
    print(f"\n[Supervisor 决策] 下一步交由: {next_node}")
    return {"next_node": next_node}
