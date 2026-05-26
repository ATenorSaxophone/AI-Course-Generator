# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import os

from dotenv import load_dotenv

from langchain_openai import OpenAI
from deepagents import create_deep_agent
from langchain.tools import tool

from mcp.server.fastmcp import FastMCP

# Get .env variables
load_dotenv()
deepseek_key = os.getenv("MY_DEEPSEEK_KEY")

#create DeepSeek model
deepseek_model = OpenAI(
    model="deepseek-v4-flash",
    open_api_base="https://api.deepseek.com",
    open_api_key=deepseek_key,
    temperature=0.7
)

@tool
def create_canvas_module():
    return 0

@tool
def create_canvas_page():
    return 0

@tool
def create_canvas_quiz():
    return 0

@tool
def create_canvas_assignment():
    return 0