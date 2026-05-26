# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import os

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool

from mcp.server.fastmcp import FastMCP

# Get .env variables
load_dotenv()
deepseek_key = os.getenv("MY_DEEPSEEK_KEY")

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