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

import docker

#Variable to keep chatbot running.
chatting = True

# Get .env variables
load_dotenv()
GammaAPI_KEY=os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.1
)

google_unverisal_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.1
)

google_gemini_lesson_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY_LESSONS"],
    temperature=0.1
)

google_gemini_quizzes_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY_QUIZZES"],
    temperature=0.1
)

google_gemini_quiz_key_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY_ANS_KEY"],
    temperature=0.1
)

google_gemini_assignment_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY_ASSIGNMENTS"],
    temperature=0.1
)

google_assignment_key_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    api_key=os.environ["MY_GOOGLE_KEY_ASSIGNMENTS_KEY"],
    temperature=0.7
)

#Create search tool using DuckDuckGoSearchRun from langchain_community
search_tool = DuckDuckGoSearchRun()

# Tools for getting context for prompts.

#Gets lesson to use as context for generations.
@tool
def get_lesson(lesson_name: int) -> str:
    """Get a HTML lesson page to use as context for a prompt to generate quizzes or assignments. This tool will NEVER use the get_assignment and get_quiz tools.
    
    Args:
        lesson_name: The name of the lesson"""
    print("entered get lesson!")

    lesson = ""
    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_lesson.html", "r", encoding="utf-8") as file:
        lesson = file.read()

    return lesson

#Gets quizzes to use as context for generations.
@tool
def get_quiz(lesson_name: int) -> str:
    """Get a HTML quiz page to use as context for a prompt to genereate quiz answer key. This tool will NEVER use the get_lesson and get_assignment tools.
    
    Args:
        lesson_name: The name of the lesson"""
    print("entered get quiz!")

    quiz = ""
    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "r", encoding="utf-8") as file:
        quiz = file.read()

    return quiz

#Gets assignment to use as context for generations.
@tool
def get_assignment(lesson_name: int) -> str:
    """Get a HTML assignment page to use as context for a prompt to generate assignment answer key. This tool will never use the get_lesson and get quiz tools.
    
    Args:
        lesson_name: The name of the lesson"""
    print("entered get assignment!")

    assignment = ""
    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "r", encoding="utf-8") as file:
        assignment = file.read()

    return assignment

# Tools for generating deliverables.

#Generates audio to be used for 
@tool
def gen_audio(lesson_name: int) -> str:
    """Use TTS to generate an audio file from a script for a video. DO NOT USE if user does not specify to.
    
    Args:
        lesson_name: The name of the lesson"""
    
    print("entered audio tool!")

    #Generates scripts for Text-to-Speech
    print("Started audio script generation!")
    subprocess.run([
        "opencode.cmd",
        "run",
        f"Create a script called 'lesson {lesson_name}_Script.txt' that covers the lesson html page. The script should not include extra characters such as asterisks. The script should be able to allow an text-to-speech generator to turn it into a 20 to 30 minute audio ,mp3 file. The txt file should be created within the folder the directory is currently in. You can only end once you are sure the .txt file has been created."
    ])

    #Gets and reads script from file explorer
    script = ""
    with open(f"./lesson {lesson_name}_Script.txt", "r", encoding="utf-8") as file:
        script = file.read()

    print("Reached Audio Generation!")
    generation = OpenAI(
        base_url="http://localhost:8880/v1", api_key="not-needed"
    )

    #Uses Text-to-Speech to create audio
    with generation.audio.speech.with_streaming_response.create(
        model="kokoro",
        voice="af_sky+af_bella", #single or multiple voicepack combo
        input= script
        ) as response:
        folder_path = Path(f"deliverables/lesson {lesson_name}")
        folder_path.mkdir(parents=True, exist_ok=True)
        response.stream_to_file(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_audio.mp3")

    print("Audio Done!")

#Generates lessons based on the topics the user gives.
@tool
def gen_lesson(prompt: str, lesson_name: int) -> str:
    """Use Google Gemini to generate a Lesson document/lesson readings in HTML using the provided template within the system prompt. DO NOT USE if user does not specify to.
    
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

    return f"Finished Lesson {lesson_name} Generation!\n60 Seconds will be taken to avoid hitting rate limits..."

#Generates quizzes from previously generated lessons
@tool
def gen_quiz(prompt: str, lesson_name: int, context: str=None) -> str:
    """Use Google Gemini to generate a Quiz document in HTML using the provided template within the system prompt. Use get_lesson tool unless user does not specify too. DO NOT USE if user does not specify to. DO NOT use the get_quiz tool as context for quiz generation. DO NOT generate an answer key on the same HTML page.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""
    
    print("entered quiz tool!")
    quiz_output = google_quiz_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "w", encoding="utf-8") as file:
        file.write(quiz_output["messages"][1].content[0]["text"])

    return f"Finished Quiz {lesson_name} Generation!\n"

#Generates answer keys for previously generated quizzes
@tool
def gen_ans_key(prompt: str, lesson_name: int, context: str) -> str:
    """Use Google Gemini to generate a quiz answer key using the provided context. Use the get_quiz tool to get context. DO NOT USE if user does not specify to.
    
    Args:
    prompt: Instructions user provide for what the Agent must generate
    lesson_name: The name of the lesson
    context: A parameter that is referenced upon to generate context. Context will come from the get_quiz tool and should be the exact same as what the output is from get_quiz tool."""

    print("entered answer key tool!")
    ans_key_output = google_quiz_key_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext:{context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_ans_key.html", "w", encoding="utf-8") as file:
        file.write(ans_key_output["messages"][1].content[0]["text"])

    return f"Finished answer key {lesson_name} Generation"

#Generates assignments based on the current lesson and instructions provided.
@tool
def gen_assignment(prompt: str, lesson_name: int, context: str=None) -> str:
    """Use Google Gemini to generate a Assignment document in HTML using the provided template within the system prompt. Use get_lesson tool unless user does not specify too. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: An OPTIONAL parameter that is referenced upon to determine generation content. Context will come from the get_lesson tool and should be the exact same as what the output is from get_lesson tool."""

    print("entered assignment tool!")
    assignment_output = google_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "w", encoding="utf-8") as file:
        file.write(assignment_output["messages"][1].content[0]["text"])
    return f"Assignment {lesson_name} generated!"

#Generates an answer key for a previously generated assignment.
@tool
def gen_assignment_key(prompt: str, lesson_name: int, context: str) -> str:
    """Use Google Gemini to generate an assignment answer key in HTML. Use the get_assignment tool unless the user specifies not to. DO NOT USE if user does not specify to.
    
    Args:
        prompt: Instructions user provide for what the Agent must generate
        lesson_name: The name of the lesson
        context: A parameter that is referenced upon to generate context. Context will come from the get_quiz tool and should be the exact same as what the output is from get_assignment tool."""

    print("entered assignment key tool!")
    assignment_key_output = google_assignment_key_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {prompt}\nContext: {context}"}]})

    folder_path = Path(f"deliverables/lesson {lesson_name}")
    folder_path.mkdir(parents=True, exist_ok=True)

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment_key.html", "w", encoding="utf-8") as file:
        file.write(assignment_key_output["messages"][1].content[0]["text"])
    return f"Assignment answer key {lesson_name} generated!"

#Generates a presentation for the lesson.
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
    """Use Remotion to generate a video using the provided context. DO NOT USE if user does not specify to. Let the AI render the video as .mp4 files. DO NOT USE the presentation.pdf files to help generate the video.
    
    Args:
        lesson_name: The name of the lesson."""
    print("Entered video generation!")

    with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_audio.mp3", "rb") as file:
        myAudio = file.read()

    os.chdir(f"deliverables/lesson {lesson_name}")
    subprocess.run(["npx.cmd", "-y", f"create-video@latest", "--yes", "--blank", f"video-lesson{lesson_name}"])
    os.chdir(f"./video-lesson{lesson_name}")
    subprocess.run(["npm.cmd", "i"])
    subprocess.run(["npx.cmd", "remotion", "skiills", "add"])
    subprocess.run(["npm.cmd", "i", "--save-exact", "@remotion/transitions@4.0.497"])
    subprocess.run(["npm.cmd", "approve-scripts", "esbuild"])

    os.chdir("./public")

    with open(f"./lesson {lesson_name}_audio.mp3", "wb") as file:
        file.write(myAudio)

    os.chdir("../")

    time.sleep(1)
    subprocess.run([
        "opencode.cmd", 
        "run", 
        f"Use Remotion best practices skill. Create a 20 to 30-minute video about lesson {lesson_name}. Make the video look visually appealing. Use transitions to go from slide to slide. DO NOT STOP until the video is completely generated. You MUST use the audio found in the public folder. If you do output the video, name it using this format: Lesson (lesson number)_video.mp4. Make sure the video aligns with the audio. Make sure each transition aligns with the next part of the audio. DO NOT RENDER THE VIDEO YET."])

    time.sleep(1)
    subprocess.run([
        "opencode.cmd",
        "run",
        "Write a reusable React component for Remotion that wraps audio. It must use the @remotion/media package to force the audio timeline to stay rigidly locked to the video frames, even if the browser drops frames or buffers during preview. Make sure it explicitly handles potential sample rate clock drift. Render the video to a .mp4 file. Find the best way to render the video efficiently, but also high-enough quality."])

    os.chdir("../../../")
    return "Video Generated!"

#Read markdown file for system prompt
with open("system_prompts/lesson_workflow.md", "r", encoding="utf-8") as file:
    lesson_prompt = file.read()

with open("system_prompts/quiz_assignment_workflow.md", "r", encoding="utf-8") as file:
    quiz_assignment_prompt = file.read()

with open("system_prompts/ans_key_workflow.md", "r", encoding="utf-8") as file:
    ans_key_prompt = file.read()

with open("system_prompts/assignment_key_workflow.md", "r", encoding="utf-8") as file:
    assignment_key_prompt = file.read()

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
    model=google_gemini_lesson_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=lesson_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google quiz agent for the course
google_quiz_agent = create_agent(
    model=google_gemini_quizzes_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=quiz_assignment_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google answer key agent for the course.
google_quiz_key_agent= create_agent(
    model=google_gemini_quiz_key_model,
    tools=[search_tool],
    system_prompt=ans_key_prompt
)

#Create google assignment agent for the course.
google_assignment_agent = create_agent(
    model=google_gemini_assignment_model,
    tools=[search_tool],
    system_prompt=quiz_assignment_prompt
)

#Create google assignment key agent for the course
google_assignment_key_agent = create_agent(
    model=google_assignment_key_model,
    tools=[search_tool],
    system_prompt=assignment_key_prompt
)

#Create syllabus agent for the course.
google_syllabus_agent = create_agent(
    model=google_gemini_model,   #Google Gemini model
    tools=[search_tool],    #Search tool for gathering dynamic information
    system_prompt=syllabus_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create Universal Agent for the course. This will be the AI used to chat with the user.
universal_agent = create_agent(
    model=google_unverisal_model,
    tools=[get_lesson, get_quiz, get_assignment, gen_lesson, gen_quiz, gen_ans_key, gen_assignment, gen_assignment_key, gen_presentation, gen_audio, gen_video], #Tool for generating HTML lessons
    system_prompt=universal_prompt #Instructions for the agent on how to create the desired deliverables from the user.
)

#Starts Kokoro TTS
client = docker.from_env()
container = client.containers.get("kokoro-tts-cpu")
container.start()
time.sleep(10)

while chatting:
    #Instructions for the user to provide.
    user_prompt = input("What deliverable do you want to generate? (Lesson, Presentation, Video, Quiz, Assignment, etc.). Type 'STOP' to stop. ")

    if user_prompt == "STOP":
        chatting = False

    else:
        #Takes user input and executes commands.
        universal_output = universal_agent.invoke({"messages": [{"role": "user", "content":f"User Prompt: {user_prompt}\nAdditional Instructions: ALWAYS use one tool at a time. If user asks to generate audio and/or video, the Get lesson tool does not need to be used. For quiz, assignment, and presentation tools, always use get lesson tool beforehand."}]})
        print("Instructions completed! Take 10 seconds to avoid rate limits.")
        time.sleep(10)
container.stop()