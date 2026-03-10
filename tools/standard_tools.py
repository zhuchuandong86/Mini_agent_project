from bs4 import BeautifulSoup
import requests
import os

from langchain_core.tools import tool
# 直接白嫖社区写好的真实搜索引擎工具
from langchain_community.tools import DuckDuckGoSearchResults

# 实例化真实的搜索工具
ddg_search = DuckDuckGoSearchResults()

@tool
def search_internet(query: str) -> str:
    """
    当需要查询互联网最新信息时调用此工具。
    """
    print(f"\n[真实 Tool 执行] 正在全网检索: {query}...")
    try:
        # 真正向互联网发送请求并获取结果
        real_result = ddg_search.invoke(query)
        return real_result
    except Exception as e:
        return f"搜索失败: {str(e)}"



from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """获取当前的真实日期和时间。在回答任何与当前时间、近期新闻有关的问题前，必须先调用此工具确认今天几号。"""
    now = datetime.now()
    return now.strftime("今天是 %Y年%m月%d日 %H:%M:%S，星期%w")

@tool
def read_webpage(url: str) -> str:
    """当需要深度阅读某个具体网页、新闻链接的完整内容时，调用此工具。"""
    print(f"\n[read_webpage Tool 执行] 正在深度抓取网页: {url}...")
    try:
        # 伪装成真实浏览器，突破反爬
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # 增加 timeout 防止卡死
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding # 解决中文乱码问题
        
        # 使用 BeautifulSoup 解析纯文本
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 杀掉所有的 js 脚本和 css 样式，只保留正文
        for script in soup(["script", "style"]):
            script.extract()
            
        text = soup.get_text(separator='\n', strip=True)
        return text[:8000] # 截断防止撑爆大模型上下文
    except Exception as e:
        return f"抓取失败: {str(e)}"


from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

repl = PythonREPL()

@tool
def execute_python_code(code: str) -> str:
    """
    当你需要进行复杂的数学计算、处理CSV数据，或者大批量处理文本时，
    你可以编写 Python 代码并用此工具执行。
    参数 code: 必须是合法的 Python 代码字符串，使用 print() 输出你需要看的结果。
    """
    print("\n[Tool Execution] 正在运行 Python 代码沙箱...")
    try:
        result = repl.run(code)
        return f"代码执行结果:\n{result}"
    except Exception as e:
        return f"代码报错:\n{str(e)}"



from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool

repl = PythonREPL()

@tool
def execute_python_code(code: str) -> str:
    """
    【终极计算与处理工具】
    当你需要进行复杂的数学计算、处理数据，或者想要通过编写脚本来解决问题时，调用此工具。
    参数 code: 必须是合法的 Python 代码字符串。
    注意：你必须在代码中使用 print() 函数将结果打印出来，否则你将无法看到输出结果！
    """
    print(f"\n[代码沙箱执行] 正在运行模型编写的 Python 脚本...")
    try:
        # 在安全的沙箱中运行模型生成的代码
        result = repl.run(code)
        if not result.strip():
            return "代码执行成功，但没有任何打印输出。请确保使用了 print()。"
        return f"执行结果:\n{result}"
    except Exception as e:
        return f"代码报错:\n{str(e)}"


        import requests
import json
from langchain_core.tools import tool

@tool
def fetch_api_data(url: str, method: str = "GET", payload: str = "{}") -> str:
    """
    当需要调用任何外部服务的 API（RESTful）时使用。
    参数 url: API 地址。
    参数 method: "GET" 或 "POST"。
    参数 payload: JSON格式的字符串，作为 POST 请求的 body。
    """
    print(f"\n[API 召唤] 正在请求接口: {method} {url} ...")
    try:
        headers = {"Content-Type": "application/json"}
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        else:
            body_dict = json.loads(payload)
            response = requests.post(url, headers=headers, json=body_dict, timeout=10)
            
        response.raise_for_status() # 检查 HTTP 错误
        return response.text[:5000]
    except Exception as e:
        return f"API 请求失败: {str(e)}"


        import os
from langchain_core.tools import tool



@tool
def read_local_file(filepath: str) -> str:
    """
    当需要读取电脑本地硬盘上的文本文件（txt, md, py, csv等）时使用此工具。
    参数 filepath: 文件的相对或绝对路径。
    """
    print(f"\n[文件读取] 正在读取本地文件: {filepath} ...")
    if not os.path.exists(filepath):
        return f"读取失败：文件 '{filepath}' 不存在。"
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return content[:15000] # 截断防止文本过大
    except Exception as e:
        return f"读取失败: {str(e)}"


import subprocess
from langchain_core.tools import tool

@tool
def execute_shell_command(command: str) -> str:
    """
    【高阶系统控制工具】
    当需要执行系统级命令、操作文件目录、安装依赖或运行外部程序时使用。
    参数 command: 需要执行的 Bash/CMD 命令语句。
    """
    print(f"\n[终端命令执行] 正在执行: {command} ...")
    try:
        # 运行系统命令并捕获输出
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return f"执行成功:\n{result.stdout}"
        else:
            return f"执行报错:\n{result.stderr}"
    except Exception as e:
        return f"命令运行失败: {str(e)}"
