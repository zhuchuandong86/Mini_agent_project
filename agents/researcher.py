import json
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from core.llm_config import get_llm
from tools.standard_tools import search_internet, read_webpage, get_current_time,execute_python_code
from core.state import AgentState

def researcher_node(state: AgentState):
    llm = get_llm()
    
    sys_prompt = """你是高级行业研究员。你需要使用工具完成深度资料收集。
    
    【你拥有的工具】
    1. `get_current_time`: 获取当前真实时间。调用格式: {"action": "get_current_time"}
    2. `search_internet`: 搜索引擎。调用格式: {"action": "search_internet", "query": "关键词"}
    3. `read_webpage`: 深度抓取网页文本。调用格式: {"action": "read_webpage", "url": "网页链接"}
    
    【极其重要的工作流规范（打组合拳）】
    第一步：【打破时间幻觉】必须先调用 `get_current_time` 确认今年是哪一年！
    第二步：【构造精准搜索】根据真实年份提取搜索关键词（千万不要把“长新闻”、“彻底读一遍”这种口语放进搜索词），调用 `search_internet`。
    第三步：【寻找有效链接】从搜索结果中，挑选最相关、信息量最大的真实 URL 链接，调用 `read_webpage` 进行深度阅读！
    第四步：【总结提炼】阅读完深度长文后，根据文章内容写出最终的深度总结。
    
    【输出规范】
    - 需要调用工具时，【务必只输出】JSON 格式，不要有任何多余的汉字或分析过程！
    - 准备汇报时，直接输出纯文本总结，并在结尾加上免责声明：“【资料已收集完毕，请 Supervisor 安排 File Manager 进行保存。】”
    """
    
    # 提取全局历史记录
    history_text = "\n".join([f"{m.type}: {m.content}" for m in state["messages"]])
    print(f'researcher history_text------------{history_text}')
    
    # 建立属于 Researcher 节点内部的“思考草稿本”
    internal_messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"【全局对话历史】\n{history_text}\n\n请开始你的思考和行动：")
    ]
    print(f'researcher internal_messages------------{internal_messages}')
    
    max_steps = 5 # 设定最大循环次数，防止它在内部无限搜索死循环
    
    for step in range(max_steps):
        response = llm.invoke(internal_messages)
        content = response.content.strip()
        
        # ==========================================
        # 1. 第一重修复：检查输出格式是否合法
        # ==========================================
        try:
            clean_content = content
            if clean_content.startswith("```json"): clean_content = clean_content[7:-3].strip()
            elif clean_content.startswith("```"): clean_content = clean_content[3:-3].strip()
                
            action_data = json.loads(clean_content)
            action = action_data.get("action")
            
        except json.JSONDecodeError as e:
            # 如果它输出的不是标准的 JSON（比如废话太多），我们不要结束，而是骂它一顿让它重写！
            if "action" not in content:
                # 如果完全没有 action 字眼，说明它可能觉得干完活了，输出了自然语言总结
                print(f"\n✅ [Researcher 调研结束] 准备向 Supervisor 提交报告。")
                return {"messages": [AIMessage(content=f"【Researcher 工作汇报】: \n{content}")]}
            else:
                # 试图调用工具但 JSON 格式写烂了，触发自我修复
                print(f"\n⚠️ [格式错误] 触发自我修复机制...")
                internal_messages.append(AIMessage(content=content))
                internal_messages.append(HumanMessage(content=f"⚠️ JSON 解析失败，错误信息: {str(e)}。请检查你的格式，不要输出多余的解释，必须且只能输出合法的 JSON 字典！"))
                continue # 直接进入下一轮让它重写

        # ==========================================
        # 2. 工具执行与第二重修复：处理运行时报错
        # ==========================================
        print(f"\n🧠 [Researcher 思考] 第 {step+1} 步: 调用工具 -> {action}")
        
        try:
            # 执行对应的工具
            if action == "get_current_time":
                tool_result = get_current_time.invoke({})
            elif action == "search_internet":
                tool_result = search_internet.invoke({"query": action_data.get("query", "")})
            elif action == "read_webpage":
                tool_result = read_webpage.invoke({"url": action_data.get("url", "")})
            elif action == "execute_python_code":
                tool_result = execute_python_code.invoke({"code": action_data.get("code", "")})
            else:
                tool_result = f"⚠️ 系统报错: 未知工具 '{action}'。请检查工具名称是否拼写正确。"
                
            # 检查工具自身返回的字符串中是否包含异常信息
            if "失败" in str(tool_result) or "报错" in str(tool_result):
                print(f"🔧 [Tool 执行异常]: {str(tool_result)[:100]}...")
                # 触发业务逻辑上的自我修复
                internal_messages.append(AIMessage(content=content))
                internal_messages.append(HumanMessage(content=f"⚠️ 工具执行遇到障碍，返回信息如下:\n{tool_result}\n\n请分析报错原因！你可以尝试更换搜索关键词，或者挑选其他搜索结果中的 URL 重新进行深度抓取。"))
            else:
                # 工具执行极其顺利
                print(f"🔧 [Tool 顺利返回 (截断预览)]: {str(tool_result)[:100]}...")
                internal_messages.append(AIMessage(content=content))
                internal_messages.append(HumanMessage(content=f"工具返回结果:\n{tool_result}\n请继续下一步操作，或直接输出最终的纯文本总结。"))
                
        except Exception as e:
            # 捕获 Python 代码层面的致命崩溃（比如网络断开、参数传错）
            print(f"❌ [系统级崩溃] 触发底层自我修复...")
            internal_messages.append(AIMessage(content=content))
            internal_messages.append(HumanMessage(content=f"⚠️ 系统执行底层崩溃，抛出异常: {str(e)}。\n你传入的参数可能有误，或者目标服务已拒绝访问。请换一种思路或换一个工具尝试。"))

    # 如果把 max_steps 耗尽了还没结束
    print(f"\n⚠️ [Researcher 调研超时] 强制结束。")
    return {"messages": [AIMessage(content="【Researcher 工作汇报】: 经过多轮搜索未能完成全部目标，已尽力收集。请 Supervisor 安排后续动作。")]}
