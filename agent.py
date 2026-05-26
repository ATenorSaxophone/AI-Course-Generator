# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain.tools import tool

from mcp.server.fastmcp import FastMCP

# Get .env variables
load_dotenv()

@tool
def create_canvas_module():
    return 0

@tool
def create_canvas_page():
    return 0