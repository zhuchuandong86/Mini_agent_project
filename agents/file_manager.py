import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from core.llm_config import get_llm
from tools.mcp_client import mcp_write_file
from core.state import AgentState

def file_manager_node(state: AgentState):
    llm = get_llm()
    
    sys_prompt = """你是文件管理专家。你需要根据之前的对话，将调研成果保存到本地。
    
    【工具说明】
    你拥有一个名为 `mcp_write_file` 的工具，可以将内容写入文件。
    
    【你的执行逻辑】
    你需要将内容写入文件时，请务必只输出如下格式的 JSON（不要有其他文字）：
    {"action": "mcp_write_file", "filename": "文件名.txt", "content": "要写入的完整报告内容"}
    
    如果写入完成，或者不需要操作文件，请直接回复“文件处理完毕”等纯文本内容。
    """
    
    history_text = "\n".join([f"{m.type}: {m.content}" for m in state["messages"]])
    print(f'file history_text----------{history_text}')
    messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"【对话历史】\n{history_text}\n\n请开始你的思考和行动：")
    ]
    print(f'file messages----------{messages}')

    response = llm.invoke(messages)
    content = response.content.strip()

    print(f'file response----------{response}')
    print(f'file content----------{content}')

    try:
        clean_content = content
        if clean_content.startswith("```json"): clean_content = clean_content[7:-3].strip()
        elif clean_content.startswith("```"): clean_content = clean_content[3:-3].strip()
            
        action_data = json.loads(clean_content)
        
        if action_data.get("action") == "mcp_write_file":
            filename = action_data.get("filename", "report.txt")
            file_content = action_data.get("content", "")
            print(f"\n[FileManager 工具调用] 准备写入文件: {filename}")
            
            # 手动执行 MCP 写入工具
            tool_result = mcp_write_file.invoke({"filename": filename, "content": file_content})
            
            messages.append(AIMessage(content=content))
            messages.append(HumanMessage(content=f"工具执行结果:\n{tool_result}\n请告诉项目经理 (Supervisor) 你的工作已完成。"))
            
            # 找到这段代码并替换 return
            final_response = llm.invoke(messages)
            # 加上【FileManager 工作汇报】前缀
            return {"messages": [AIMessage(content=f"【FileManager 工作汇报】: {final_response.content}")]}
            
    except Exception:
        pass
        
    # 这里的 return 也要改
    return {"messages": [AIMessage(content=f"【FileManager 工作汇报】: {content}")]}
