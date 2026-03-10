import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm():
    """
    获取全局统一的大模型实例。
    这里使用的是 langchain_openai，它可以完美适配绝大多数企业内网的兼容接口。
    """
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        temperature=0.1 # Agent 任务建议较低温度，保证输出的稳定性与逻辑性
    )
