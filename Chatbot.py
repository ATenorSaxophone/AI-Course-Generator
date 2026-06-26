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

# Tools for getting context for prompts.
@tool
def get_lesson(lesson_num: int) -> str:
    """Get a HTML lesson page to use as context for a prompt to generate quizzes or assignments. This tool will NEVER use the get_lesson tool.
    
    Args:
        lesson_num: The number of the lesson"""
    print("entered get lesson!")

    lesson = ""
    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_lesson.html", "r", encoding="utf-8") as file:
        lesson = file.read()

    return lesson


# Tools for generating lessons, assignments, and quizzes.
@tool
def gen_lesson(prompt: str, lesson_num: int) -> str:
    """Use Google Gemini to generate a Lesson document in HTML using the provided template within the system prompt.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_num: The number of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content"""
    
    print("entered lesson tool!")
    lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_num}\nPrompt: {prompt}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_num}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_lesson.html", "w", encoding="utf-8") as file:
        file.write(lesson_output["messages"][1].content[0]["text"])

    return f"Finished Lesson {lesson_num} Generation!\n60 Seconds will be taken to avoid hitting rate limits..."


@tool
def gen_quiz(prompt: str, lesson_num: int, context: str=None) -> str:
    """Use Google Gemini to generate a Quiz document in HTML using the provided template within the system prompt. This tool should run if user answers Yes/Y to Context Preference.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_num: The number of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""
    
    print("entered quiz tool!")
    quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_num}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_num}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_quiz.html", "w", encoding="utf-8") as file:
        file.write(quiz_output["messages"][1].content[0]["text"])

    return f"Finished Quiz {lesson_num} Generation!\n60 Seconds will be taken to avoid hitting rate limits"


@tool
def gen_assignment(prompt: str, lesson_num: int, context: str=None) -> str:
    """Use Google Gemini to generate a Assignment document in HTML using the provided template within the system prompt.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_num: The number of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""

    print("entered assignment tool!")
    assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_num}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_num}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_assignment.html", "w", encoding="utf-8") as file:
        file.write(assignment_output["messages"][1].content[0]["text"])

    return f"Assignment {lesson_num} generated!\n60 Seconds will be taken to avoid hitting rate limits"


@tool
def gen_presentation(lesson_num: int, context: str) -> str:
    """Use Gamma AI to generated presentations in a .pdf file. The AI should use the get_lesson tool to get the context needed to generate the presentations.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_num: The number of the lesson
        context: A parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""
    print("entered presentation tool!")
    response = requests.post(
    "https://public-api.gamma.app/v1.0/generations",
    headers={"X-API-KEY": GammaAPI_KEY, "Content-Type": "application/json"},
    data=json.dumps({
        "textMode": "generate",
        "format": "presentation",
        "cardSplit": "auto",
        "exportAs": "pdf",
        "inputText": context,
        "additionalInstructions": presentation_prompt,
        "numCards": 13,
        "themeId": "electric",
        "textOptions": {
            "amount": "detailed",
            "language": "en",
            "tone": "professional",
            "audience": "college students"
            },
        "imageOptions": {
            "model": "flux-2-pro",
            "source": "aiGenerated",
            "style": "photorealistic, professional"
            },
        "cardOptions": {
            "dimensions": "16x9",
            },
        "sharingOptions": {
            "workspaceAccess": "view",
            "externalAccess": "noAccess"
            },
        })
    )

    data = response.json()
    print(data)
    timeout = 0
    x=1

    print(data.get("generationId"))

    while True:
        time.sleep(5)  # Wait for 5 seconds before polling again

        status_response = requests.get(
            f"https://public-api.gamma.app/v1.0/generations/{data.get('generationId')}",
            headers={"X-API-KEY": GammaAPI_KEY}
        )

        if status_response.status_code == 200 and status_response.json().get("status") == "completed":
            with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_presentation.pdf", "wb") as file:
                file.write(requests.get(status_response.json().get("exportUrl")).content)
            return f"Presentation Generated!\n60 Seconds will be taken to avoid hitting rate limits"

        elif status_response.status_code != 200:
            return f"Error checking generation status: {status_response.text}"
        
        elif status_response.status_code == 200 and timeout > 300:  # Timeout after 5 minutes
            return "Generation is taking too long. Timing out."

        print(f"-----------------------------{x}")
        print("Generation status:", status_response.json().get("status"))
        print("Status code:", status_response.status_code)
        x += 1
        timeout += 5

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
    tools=[get_lesson, gen_lesson, gen_quiz, gen_assignment, gen_presentation], #Tool for generating HTML lessons
    system_prompt=universal_prompt #Instructions for the agent on how to create the desired deliverables from the user.
)

user_prompt = input("What deliverable do you want to generate? (Lesson, Presentation, Video, Quiz, Assignment)")
user_lesson_num = input("What lesson number is this lesson?")

universal_output = universal_agent.invoke({"messages": [{"role": "user", "content":f"Lesson Number: {user_lesson_num}\n\nUser Prompt: {user_prompt}\nAdditional Instructions: Only use each NECESSARY tool ONCE."}]})
print("Deliverable Completed!")
print("Taking 60 Seconds to avoid hitting rate limits!")
time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits