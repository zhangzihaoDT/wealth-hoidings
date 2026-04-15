import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from .research_tools import wikipedia_search_tool

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY", ""),
    base_url="https://api.deepseek.com"
)

def call_deepseek(prompt: str, system_prompt: str = "You are a helpful assistant.") -> str:
    """Helper to call DeepSeek 3.2 model."""
    if not client.api_key:
        return "[Mock DeepSeek Response] API key not found. Please set DEEPSEEK_API_KEY in .env"
    
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[DeepSeek Error] {e}"

def research_agent(topic: str) -> str:
    """Conducts research using Wikipedia and DeepSeek."""
    print(f"[Research Agent] Searching for: {topic}")
    
    wiki_res = wikipedia_search_tool(topic)
    
    prompt = f"Based on this Wikipedia information about '{topic}':\n\n{wiki_res}\n\nPlease summarize the key points and provide a brief analysis."
    summary = call_deepseek(prompt, "You are a professional research assistant.")
    
    return (
        f"--- Research Data on {topic} ---\n\n"
        f"Wikipedia Summary:\n{wiki_res}\n\n"
        f"DeepSeek Analysis:\n{summary}\n"
    )

def writer_agent(research_data: str) -> str:
    """Writes a draft based on research data using DeepSeek."""
    print(f"[Writer Agent] Drafting report...")
    prompt = f"Write a comprehensive and structured draft report based on the following research data:\n\n{research_data}"
    draft = call_deepseek(prompt, "You are an expert report writer.")
    return draft

def editor_agent(draft: str) -> str:
    """Edits and polishes the draft using DeepSeek."""
    print(f"[Editor Agent] Editing report...")
    prompt = f"Please edit and polish the following draft report for clarity, tone, and formatting. Make it look professional:\n\n{draft}"
    final_report = call_deepseek(prompt, "You are a professional editor.")
    print(f"[Editor Agent] Editing complete!")
    return final_report
