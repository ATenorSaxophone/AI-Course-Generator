import os
from langchain.agents import create_anthropic_agent
from langchain.chat_models import ChatAnthropic
from langchain_core.tools import Tool

from mcp.server.fastmcp import FastMCP