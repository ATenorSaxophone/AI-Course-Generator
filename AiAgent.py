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
import shutil

#Save .cache location
cache = Path.home()/".cache"/"opencode"

# Get .env variables
load_dotenv()
GammaAPI_KEY=os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
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

google_gemini_ans_key_model = ChatGoogleGenerativeAI(
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

#read user prompts
with open("prompts.json", "r", encoding="utf-8") as file:
    user_prompts = json.load(file)

#Create agents
google_lesson_agent = create_agent(
    model=google_gemini_lesson_model,   #Google Gemini model
    system_prompt=lesson_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google quiz agent for the course
google_quiz_agent = create_agent(
    model=google_gemini_quizzes_model,   #Google Gemini model
    system_prompt=quiz_assignment_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

#Create google answer key agent for the course.
google_ans_key_agent= create_agent(
    model=google_gemini_ans_key_model,
    system_prompt=ans_key_prompt
)

#Create google assignment agent for the course.
google_assignment_agent = create_agent(
    model=google_gemini_assignment_model,
    system_prompt=quiz_assignment_prompt
)

google_assignment_key_agent = create_agent(
    model=google_assignment_key_model,
    system_prompt=assignment_key_prompt
)

#Create syllabus agent for the course.
google_syllabus_agent = create_agent(
    model=google_gemini_model,   #Google Gemini model
    system_prompt=syllabus_prompt     #Instructions for the agent on how to create the Canvas Class and Canvas components.
)

client = docker.from_env()
container = client.containers.get("kokoro-tts-cpu")
container.start()
time.sleep(10)

for lesson_name in range(17,17):

    curr_lesson = user_prompts[f"lesson {lesson_name}"]

    if curr_lesson.get("lesson prompt"):
        print("entered lesson!")
        #Generate Lesson readings for the course
        lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {curr_lesson["lesson prompt"]}"}]})

        folder_path = Path(f"deliverables/lesson {lesson_name}")
        folder_path.mkdir(parents=True, exist_ok=True)

        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_lesson.html", "w", encoding="utf-8") as file:
            file.write(lesson_output["messages"][1].content[0]["text"])


        #Get Lesson for further generations
        lesson = ""
        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_lesson.html", "r", encoding="utf-8") as file:
            lesson = file.read()


    if curr_lesson.get("quiz prompt"):
        print("entered quiz!")

        if lesson_name == 16:

            lesson_content = ""
            for lesson_num in range(1, 15):
                with open(f"deliverables/{f"lesson {lesson_num}"}/{f"lesson {lesson_num}"}_lesson.html", "r", encoding="utf-8") as file:
                    lesson_content += "\n\n" + file.read()

            final_exam_output = google_quiz_agent.invoke({"messages": [{"role": "user", "content": f"Content: {lesson_content} \n\n Prompt: {curr_lesson["quiz prompt"]}"}]})

            folder_path = Path(f"deliverables/lesson {lesson_name}")
            folder_path.mkdir(parents=True, exist_ok=True)

            with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "w", encoding="utf-8") as file:
                file.write(final_exam_output["messages"][1].content[0]["text"])

        else:
            #Generate quizzes for the course
            quiz_output = google_quiz_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {curr_lesson["quiz prompt"]}\nContext: {lesson}"}]})

            folder_path = Path(f"deliverables/lesson {lesson_name}")
            folder_path.mkdir(parents=True, exist_ok=True)

            with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "w", encoding="utf-8") as file:
                file.write(quiz_output["messages"][1].content[0]["text"])

        #Get Quizzes for further generations
        quiz = ""
        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_quiz.html", "r", encoding="utf-8") as file:
            quiz = file.read()


        #Generate Answer key for the quizzes
        print("entered quiz key!")
        ans_key_output = google_ans_key_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: Generate the answer key for quiz {lesson_name}\nContext:{quiz}"}]})

        folder_path = Path(f"deliverables/lesson {lesson_name}")
        folder_path.mkdir(parents=True, exist_ok=True)

        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_ans_key.html", "w", encoding="utf-8") as file:
            file.write(ans_key_output["messages"][1].content[0]["text"])


    if curr_lesson.get("assignment prompt"):
        print("entered assignment!")
        #Generate assignments for the course
        if lesson_name == 15:
            assignment_output = google_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {curr_lesson["assignment prompt"]}"}]})    

            folder_path = Path(f"deliverables/lesson {lesson_name}")
            folder_path.mkdir(parents=True, exist_ok=True)

            with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "w", encoding="utf-8") as file:
                file.write(assignment_output["messages"][1].content[0]["text"])

        else:
            assignment_output = google_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: {curr_lesson["assignment prompt"]}\nContext: {lesson}"}]})

            folder_path = Path(f"deliverables/lesson {lesson_name}")
            folder_path.mkdir(parents=True, exist_ok=True)

            with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "w", encoding="utf-8") as file:
                file.write(assignment_output["messages"][1].content[0]["text"])

        #Get assignment for future generations
        assignment = ""
        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment.html", "r", encoding="utf-8") as file:
            assignment = file.read()


        #Generate answer key for assignments
        print("entered assignment key!")
        assignment_key_output = google_assignment_key_agent.invoke({"messages": [{"role": "user", "content": f"Lesson Num: {lesson_name}\nPrompt: Create an answer key for assignment {lesson_name}\nContext: {assignment}"}]})

        folder_path = Path(f"deliverables/lesson {lesson_name}")
        folder_path.mkdir(parents=True, exist_ok=True)

        with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_assignment_key.html", "w", encoding="utf-8") as file:
            file.write(assignment_key_output["messages"][1].content[0]["text"])


    if curr_lesson["presentation?"] == "yes":
        print("entered presentation!")
        #Generate presentation for the course
        response = requests.post(
            "https://public-api.gamma.app/v1.0/generations",
            headers={"X-API-KEY": GammaAPI_KEY, "Content-Type": "application/json"},
            data=json.dumps({
                "textMode": "generate",
                "format": "presentation",
                "cardSplit": "auto",
                "exportAs": "pdf",
                "inputText": f"lesson name: {lesson_name}\ncontext: {lesson}",
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

        running = True
        while running:
            time.sleep(5)  # Wait for 5 seconds before polling again

            status_response = requests.get(
                f"https://public-api.gamma.app/v1.0/generations/{data.get('generationId')}",
                headers={"X-API-KEY": GammaAPI_KEY}
            )

            if status_response.status_code == 200 and status_response.json().get("status") == "completed":
                with open(f"deliverables/lesson {lesson_name}/lesson {lesson_name}_presentation.pdf", "wb") as file:
                    file.write(requests.get(status_response.json().get("exportUrl")).content)
                running = False

            print(f"-----------------------------{x}")
            print("Generation status:", status_response.json().get("status"))
            print("Status code:", status_response.status_code)
            x += 1
            timeout += 5

    if curr_lesson["video?"] == "yes":
        print("entered audio script!")
        #Start generation for audio script
    os.chdir(f"deliverables/lesson {lesson_name}")
    subprocess.run([
        "opencode.cmd",
        "run",
        f"Create a script called 'lesson {lesson_name}_Script.txt' that covers the lesson html page. The script should not include extra characters such as asterisks. The script should be able to allow an text-to-speech generator to turn it into a 20 to 30 minute audio ,mp3 file. The txt file should be created within the folder the directory is currently in. You can only end once you are sure the .txt file has been created."
    ])
    time.sleep(20)

    script = ""
    with open(f"./lesson {lesson_name}_Script.txt", "r", encoding="utf-8") as file:
        script = file.read()

    #Generate audio for course
    print("entered audio!")
    generation = OpenAI(
            base_url="http://localhost:8880/v1", api_key="not-needed"
        )
    
    with generation.audio.speech.with_streaming_response.create(
        model="kokoro",
        voice="af_sky+af_bella", #single or multiple voicepack combo
        input= script
        ) as response:
        response.stream_to_file(f"./lesson {lesson_name}_audio.mp3")
    time.sleep(20)


    #Generate Videos with audio for course
    print("entered video!")
    with open(f"./lesson {lesson_name}_audio.mp3", "rb") as file:
            myAudio = file.read()

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
        f"Use Remotion best practices skill. Create a 20 to 30-minute video about lesson {lesson_name}. Make the video look visually appealing. Use transitions to go from slide to slide. DO NOT STOP until the video is completely generated. You MUST use the audio found in the public folder. If you do output the video, name it using this format: Lesson (lesson number)_video.mp4. Make sure the video aligns with the audio. Make sure each transition aligns with the next part of the audio. DO NOT RENDER ANYTHING. Keep the requests to a minimum. Set the ID of the video to 'Lesson{lesson_name}'"])

    subprocess.run([
        "npx.cmd",
        "remotion",
        "render",
        f"Lesson{lesson_name}"])

    os.chdir("../../../")

    time.sleep(10)

    if cache.exists():
        shutil.rmtree(cache)

    time.sleep(10)

#Get assignments as context for the syllabus
assignments = ""
for lesson_num in range(1, 15):
    with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_assignment.html", "r", encoding="utf-8") as file:
        assignments += "\n\n" + file.read()

#Syllabus generation
print("entered syllabus!")
syllabus_output = google_syllabus_agent.invoke({"messages": [{"role": "user", "content": f"{user_prompts["syllabus"]["syllabus"]}\nContext: {assignments}"}]})

folder_path = Path(f"deliverables/syllabus")
folder_path.mkdir(parents=True, exist_ok=True)

with open(f"deliverables/syllabus/syllabus.html", "w", encoding="utf-8") as file:
    file.write(syllabus_output["messages"][1].content[0]["text"])

#Get syllabus for agreement form
syllabus = ""
with open(f"deliverables/syllabus/syllabus.html", "r", encoding="utf-8") as file:
    syllabus = file.read()

#Agreement form generation
print("entered agreement form!")
agreement_form_output = google_syllabus_agent.invoke({"messages": [{"role": "user", "content": user_prompts["syllabus"]["agreement form"]}]})

folder_path = Path(f"deliverables/syllabus")
folder_path.mkdir(parents=True, exist_ok=True)

with open(f"deliverables/syllabus/agreement_form.html", "w", encoding="utf-8") as file:
    file.write(agreement_form_output["messages"][1].content[0]["text"])

container.stop()