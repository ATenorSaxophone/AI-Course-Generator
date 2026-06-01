# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import json
import os
import time

from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
# from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Get .env variables
load_dotenv()
google_key = os.getenv("MY_GOOGLE_KEY")

#Create Google AI Studio model
google_lesson_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.7
)

google_quiz_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.7
)

google_presentation_model = ChatGoogleGenerativeAI(
    model="gemini-3-pro-image",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.7
)

#Create search tool using DuckDuckGoSearchRun from langchain_community
search_tool = DuckDuckGoSearchRun()

#Read markdown file for system prompt
with open("system_prompts/lesson_workflow.md", "r", encoding="utf-8") as file:
    lesson_prompt = file.read()

with open("system_prompts/quiz_assignment_workflow.md", "r", encoding="utf-8") as file:
    quiz_assignment_prompt = file.read()

with open("system_prompts/presentation_workflow.md", "r", encoding="utf-8") as file:
    presentation_prompt = file.read()

with open("system_prompts/syllabus_workflow.md", "r", encoding="utf-8") as file:
    syllabus_prompt = file.read()

#Create google lesson agent
google_lesson_agent = create_agent(
    model=google_lesson_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=lesson_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google quiz and assignmentagent
google_quiz_assignment_agent = create_agent(
    model=google_quiz_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=quiz_assignment_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google presentation agent for lessons.
google_presentation_agent = create_agent(
    model=google_presentation_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=presentation_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create syllabus agent for the course.
google_syllabus_agent = create_agent(
    model=google_lesson_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=syllabus_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#get prompts from prompts.json file
with open("prompts.json", "r", encoding="utf-8") as file:
    prompts = json.load(file)

#1 lesson test code
# output = google_chat_agent.invoke({"messages": [{"role": "user", "content": prompts["lesson 1"]["lesson prompt"]}]})
# print(output)
# with open("out.html", "w", encoding="utf-8") as file:
#     file.write(output["messages"][1].content[0]["text"])


#Run agent with prompt inputs and print outputs
for key, value in prompts.items():

    if key == "lesson 15":
        final_project_prompt = value["final presentation prompt"]
    
        final_project_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": final_project_prompt}]})
        print("Final Project Finished!")
        print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        print(f"Final Project Output for {key}:\n{final_project_output}\n")

    elif key == "lesson 16":
        final_exam_prompt = value["final exam prompt"]
    
        final_exam_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": final_exam_prompt}]})
        print("Final Exam Finished!")
        print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        print(f"Final Exam Output for {key}:\n{final_exam_output}\n")

    else:
        lesson_prompt = value["lesson prompt"]
        quiz_prompt = value["quiz prompt"]
        assignment_prompt = value["assignment prompt"]
        
        # Run the agent with the combined prompt
        lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": lesson_prompt}]})
        print("Lesson Finished!")
        print("Waiting for 60 seconds before invoking the quiz and assignment prompts to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        presentation_output = google_presentation_agent.invoke({"messages": [{"role": "user", "content": lesson_prompt["messages"][1].content[0]["text"]}]})
        print("Presentation Finished!")
        print("Waiting for 60 seconds before invoking the quiz and assignment prompts to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": lesson_prompt["messages"][1].content[0]["text"] + "\n\n" + quiz_prompt}]})
        print("Quiz Finished!")
        print("Waiting for 60 seconds before invoking the assignment prompt to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": lesson_prompt["messages"][1].content[0]["text"] + "\n\n" + assignment_prompt}]})
        print("Assignment Finished!")
        print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        print(f"Readings Output for {key}:\n{lesson_output}\n")
        print(f"Quiz Output for {key}:\n{quiz_output}\n")
        print(f"Assignment Output for {key}:\n{assignment_output}\n")