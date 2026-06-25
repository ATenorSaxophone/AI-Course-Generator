import json
import os

from dotenv import load_dotenv
import time, requests

from pathlib import Path

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Get .env variables
load_dotenv()
google_key = os.getenv("MY_GOOGLE_KEY")
HeyGenAPI_KEY = os.getenv("MY_HEYGEN_KEY")
GammaAPI_KEY = os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.1
)

google_unverisal_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.1
)

#Create search tool using DuckDuckGoSearchRun from langchain_community
search_tool = DuckDuckGoSearchRun()

# Tools for generating lessons, assignments, and quizzes.
@tool
def gen_lesson(prompt: str, lesson_num: int) -> str:
    """Use Google Gemini to generate a Lesson document in HTML using the provided template within the system prompt.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_num: The number of the lesson"""
    
    print("entered lesson tool!")
    lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    folder_path = Path(f"deliverables/lesson {lesson_num}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_lesson.html", "w", encoding="utf-8") as file:
        file.write(lesson_output["messages"][1].content[0]["text"])

    return f"Finished Lesson {lesson_num} Generation!\n60 Seconds will be taken to avoid hitting rate limits..."

#Read markdown file for system prompt
with open("system_prompts/lesson_workflow.md", "r", encoding="utf-8") as file:
    lesson_prompt = file.read()

with open("system_prompts/quiz_assignment_workflow.md", "r", encoding="utf-8") as file:
    quiz_assignment_prompt = file.read()

with open("system_prompts/presentation_workflow.md", "r", encoding="utf-8") as file:
    presentation_prompt = file.read()

with open("system_prompts/syllabus_workflow.md", "r", encoding="utf-8") as file:
    syllabus_prompt = file.read()

with open("system_prompts/video_workflow.md", "r", encoding="utf-8") as file:
    video_prompt = file.read()

with open("system_prompts/universal_workflow.md", "r", encoding="utf-8") as file:
    universal_prompt = file.read()


#Create google lesson agent
google_lesson_agent = create_agent(
    model=google_gemini_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=lesson_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google quiz and assignmentagent
google_quiz_assignment_agent = create_agent(
    model=google_gemini_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=quiz_assignment_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create syllabus agent for the course.
google_syllabus_agent = create_agent(
    model=google_gemini_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=syllabus_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create Universal Agent for the course.
universal_agent = create_agent(
    model=google_unverisal_model,
    tools=[gen_lesson], #Tool for generating HTML lessons
    system_prompt=universal_prompt #Instructions for the agent on how to create the desired deliverables from the user.
)

user_prompt = input("What lesson do you want to generate?")
user_lesson_num = input("What lesson number is this lesson?")

universal_output = universal_agent.invoke({"messages": [{"role": "user", "content":f"Lesson Number: {user_lesson_num}\n\nUser Prompt: {user_prompt}"}]})
print(universal_output["messages"][1].content[0]["text"])
time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits