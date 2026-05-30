# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import json
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

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

#Create search tool using DuckDuckGoSearchRun from langchain_community
search_tool = DuckDuckGoSearchRun()

#Read markdown file for system prompt
with open("workflow.md", "r", encoding="utf-8") as file:
    system_prompt = file.read()

#create agent with tools and deepseek model
agent = create_deep_agent(
    model=deepseek_model,   #DeepSeek model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=system_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#get prompts from prompts.json file
with open("prompts.json", "r", encoding="utf-8") as file:
    prompts = json.load(file)

#Run agent with prompt inputs and print outputs
for key, value in prompts.items():

    if key == "lesson 15":
        final_project_prompt = value["final presentation prompt"]
        print(final_project_prompt)
    
        final_project_output = agent.invoke({"messages": [{"role": "user", "content": final_project_prompt}]})
        print(f"Final Project Output for {key}:\n{final_project_output}\n")

    elif key == "lesson 16":
        final_exam_prompt = value["final exam prompt"]
        print(final_exam_prompt)
    
        final_exam_output = agent.invoke({"messages": [{"role": "user", "content": final_exam_prompt}]})
        print(f"Final Exam Output for {key}:\n{final_exam_output}\n")

    else:
        lesson_prompt = value["lesson prompt"]
        quiz_prompt = value["quiz prompt"]
        assignment_prompt = value["assignment prompt"]
        
        # Run the agent with the combined prompt
        lesson_output = agent.invoke({"messages": [{"role": "user", "content": lesson_prompt}]})
        quiz_output = agent.invoke({"messages": [{"role": "user", "content": quiz_prompt}]})
        assignment_output = agent.invoke({"messages": [{"role": "user", "content": assignment_prompt}]})
    
        print(f"Readings Output for {key}:\n{lesson_output}\n")
        print(f"Quiz Output for {key}:\n{quiz_output}\n")
        print(f"Assignment Output for {key}:\n{assignment_output}\n")