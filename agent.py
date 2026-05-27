# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from mcp.server.fastmcp import FastMCP

# Get .env variables
load_dotenv()
deepseek_key = os.getenv("MY_DEEPSEEK_KEY")

#create DeepSeek model
deepseek_model = ChatOpenAI(
    model="deepseek-v4-flash",
    base_url="https://api.deepseek.com",
    api_key=os.environ["MY_DEEPSEEK_KEY"],
    temperature=0.7
)

@tool                    #Type hints for create_canvas_module tool
def create_canvas_module(course_id: str, module_name: str) -> str:
    #Docstring for create_canvas_module tool
    """
    Creates a module in a Canvas Instructure course.
    
    Parameters:
    - course_id: The ID of the Canvas course where the module will be created.
    - module_name: The name of the module to be created.

    Returns:
    - A string confirming the creation of the module with the course ID and module name.
    """

    # Here you would add the actual implementation to interact with the Canvas API to create a module.

    #return a confirmation message for the created module
    return f"Canvas module created for course: {course_id}, module: {module_name}"

@tool
def create_canvas_page(canvas_id: str, page_title: str, page_content: str) -> str:
    #Docstring for create_canvas_page tool
    """
    Creates a page in a Canvas Instructure course.

    Parameters:
    - canvas_id: The ID of the Canvas course where the page will be created.
    - page_title: The title of the page to be created.
    - page_content: The content of the page to be created.

    Returns:
    - A string confirming the creation of the page with the canvas ID and page title.
    """

    # Here you would add the actual implementation to interact with the Canvas API to create a page.

    #return a confirmation message for the created page
    return f"Canvas page created for canvas: {canvas_id}, page: {page_title}"

# @tool
# def create_canvas_quiz():
#     return 0

# @tool
# def create_canvas_assignment():
#     return 0

#Create search tool using Tavily Search Results
search_tool = DuckDuckGoSearchRun()

#Read markdown file for system prompt
with open("workflow.md", "r") as file:
    system_prompt = file.read()

#create agent with tools and deepseek model
agent = create_deep_agent(
    model=deepseek_model,
    tools=[
        create_canvas_module,
        create_canvas_page,
    #     create_canvas_quiz,
    #     create_canvas_assignment,
        search_tool
    ],
    system_prompt=system_prompt
)