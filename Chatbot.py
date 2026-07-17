import json
import os

from dotenv import load_dotenv
import time, requests

from pathlib import Path
import subprocess

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

from google import genai
from openai import OpenAI

# from TTS.api import TTS

# Get .env variables
load_dotenv()
google_key = os.getenv("MY_GOOGLE_KEY")
GammaAPI_KEY = os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
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
def get_lesson(lesson_name: int) -> str:
    """Get a HTML lesson page to use as context for a prompt to generate quizzes or assignments. This tool will NEVER use the get_lesson tool.
    
    Args:
        lesson_name: The name of the lesson"""
    print("entered get lesson!")

    lesson = ""
    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_lesson.html", "r", encoding="utf-8") as file:
        lesson = file.read()

    return lesson

@tool
def gen_audio(lesson_name: int) -> str:
    """Use TTS to generate an audio file from a script for a video. DO NOT USE if user does not specify to.
    
    Args:
        lesson_name: The name of the lesson"""
    
    print("entered audio tool!")
    upload = genai.Client(api_key=os.environ["MY_GOOGLE_KEY"])

    myfile = upload.files.upload(file=f"deliverables/lesson {lesson_name}/lesson {lesson_name}_presentation.pdf")

    script = upload.interactions.create(
        model="gemini-2.5-flash",
        input=[
            {"type": "text", "text": "Create an audio prompt of the following presentation. Do not provide instructions, only words that are to be spoken. Try to make the script long enough to cover 20 minutes of audio and no more than 30 minutes of audio. The final output should only include letters and punctuation (periods, commas, apostrophe, etc.). The final output should not include characters like asterisks."},
            {"type": "document", "uri": myfile.uri, "mime_type": myfile.mime_type}
        ]
    )

    upload.files.delete(name=myfile.name)

    generation = OpenAI(
        base_url="http://localhost:8880/v1", api_key="not-needed"
    )

    with generation.audio.speech.with_streaming_response.create(
        model="kokoro",
        voice="af_sky+af_bella", #single or multiple voicepack combo
        input= script.output_text
        ) as response:
        folder_path = Path(f"deliverables/lesson {lesson_name}")
        folder_path.mkdir(parents=True, exist_ok=True)
        response.stream_to_file(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_audio.mp3")

# Tools for generating lessons, assignments, and quizzes.
@tool
def gen_lesson(prompt: str, lesson_name: int) -> str:
    """Use Google Gemini to generate a Lesson document in HTML using the provided template within the system prompt. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content"""
    
    print("entered lesson tool!")
    lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_lesson.html", "w", encoding="utf-8") as file:
        file.write(lesson_output["messages"][1].content[0]["text"])
    print("Taking 60 seconds to avoid rate limits!")
    time.sleep(60)

    return f"Finished Lesson {lesson_name} Generation!\n60 Seconds will be taken to avoid hitting rate limits..."


@tool
def gen_quiz(prompt: str, lesson_name: int, context: str=None) -> str:
    """Use Google Gemini to generate a Quiz document in HTML using the provided template within the system prompt. This tool should run if user answers Yes/Y to Context Preference. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""
    
    print("entered quiz tool!")
    quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "w", encoding="utf-8") as file:
        file.write(quiz_output["messages"][1].content[0]["text"])
    print("Taking 60 seconds to avoid rate limits!")
    time.sleep(60)

    return f"Finished Quiz {lesson_name} Generation!\n60 Seconds will be taken to avoid hitting rate limits"


@tool
def gen_assignment(prompt: str, lesson_name: int, context: str=None) -> str:
    """Use Google Gemini to generate a Assignment document in HTML using the provided template within the system prompt. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""

    print("entered assignment tool!")
    assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "w", encoding="utf-8") as file:
        file.write(assignment_output["messages"][1].content[0]["text"])
    print("Taking 60 seconds to avoid rate limits!")
    time.sleep(60)

    return f"Assignment {lesson_name} generated!\n60 Seconds will be taken to avoid hitting rate limits"


@tool
def gen_presentation(lesson_name: int, context: str) -> str:
    """Use Gamma AI to generated presentations in a .pdf file. The AI should use the get_lesson tool to get the context needed to generate the presentations. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
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
        "inputText": f"lesson name: {lesson_name}\ncontext: {context}",
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
            with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_presentation.pdf", "wb") as file:
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

#Generates video using remotion and TypeScript react.
@tool
def gen_video(lesson_name: int) -> str:
    """Use Remotion to generate a video using the provided context. DO NOT USE if user does not specify to.
    
    Args:
        lesson_name: The name of the lesson.
        context: A parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""

    print("Entered video generation!")

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_audio.mp3", "rb") as file:
        myAudio = file.read()

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_presentation.pdf", "rb") as file:
        myPres = file.read()

    os.chdir(f"deliverables/lesson {lesson_name}")
    subprocess.run(["npx.cmd", "-y", f"create-video@latest", "--yes", "--blank", f"video-lesson{lesson_name}"])
    os.chdir(f"./video-lesson{lesson_name}")
    subprocess.run(["npm.cmd", "i"])
    subprocess.run(["npx.cmd", "remotion", "skiills", "add"])
    subprocess.run(["npm.cmd", "approve-scripts", "esbuild@0.28.1"])
    subprocess.run(["npm.cmd", "i", "--save-exact", "@remotion/transitions@4.0.490"])

    os.chdir("./public")

    with open(f"./lesson {lesson_name}_audio.mp3", "wb") as file:
        file.write(myAudio)

    with open(f"./lesson {lesson_name}_presentation.pdf", "wb") as file:
        file.write(myPres)

    os.chdir("../")

    subprocess.run([
        "opencode.cmd", 
        "run", 
        f"'Use Remotion best practices skill. Create a 20 to-minute video about lesson {lesson_name}. Use the presentation and audio files found in the public folder to help create the video. Make the video look visually appealing. Use transitions to go from slide to slide. DO NOT STOP until the video is completely generated. You MUST use the audio found in the public folder. If you do output the video, name it using this format: Lesson (lesson number)_video.mp4. DO NOT ALLOW each part of the audio file to overlap with each part of the video. Make sure each transition aligns with the next part of the audio.'"])

    return "Video Generated!"

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
    tools=[get_lesson, gen_lesson, gen_quiz, gen_assignment, gen_presentation, gen_audio, gen_video], #Tool for generating HTML lessons
    system_prompt=universal_prompt #Instructions for the agent on how to create the desired deliverables from the user.
)

user_prompt = input("What deliverable do you want to generate? (Lesson, Presentation, Video, Quiz, Assignment)")

universal_output = universal_agent.invoke({"messages": [{"role": "user", "content":f"User Prompt: {user_prompt}\nAdditional Instructions: Only use each NECESSARY tool ONCE. ALWAYS use one tool at a time."}]})
print("Deliverable Completed!")