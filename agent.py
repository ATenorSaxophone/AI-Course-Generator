# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import json
import os
import time

from dotenv import load_dotenv
import time, requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
# from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

# Get .env variables
load_dotenv()
google_key = os.getenv("MY_GOOGLE_KEY")
HeyGenAPI_KEY = os.getenv("MY_HEYGEN_KEY")
GammaAPI_KEY = os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_lesson_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.7
)

google_quiz_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
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

with open("system_prompts/video_workflow.md", "r", encoding="utf-8") as file:
    video_prompt = file.read()

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
        user_lesson_prompt = value["lesson prompt"]
        user_quiz_prompt = value["quiz prompt"]
        user_assignment_prompt = value["assignment prompt"]

        # Run the agent with the combined prompt
        lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": user_lesson_prompt}]})
        print("Lesson Finished!")
        print("Waiting for 60 seconds before invoking the quiz and assignment prompts to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        #Create presentation for the lesson using the presentation agent and the user_lesson_prompt as the base content for the presentation.
        response = requests.post(
            "https://public-api.gamma.app/v1.0/generations",
            headers={"X-API-KEY": GammaAPI_KEY, "Content-Type": "application/json"},
            data=json.dumps({
            "textMode": "generate",
            "format": "presentation",
            "cardSplit": "auto",
            "exportAs": "pdf",
            "inputText": lesson_output["messages"][1].content[0]["text"],
            "additionalInstructions": "Make it visually engaging and informative, with a professional design suitable for marketing executives. Use relevant visuals and graphics to complement the content of the slides. Add speaker notes for each slide that provide additional context and information for the presenter. Ensure that the presentation effectively conveys the key points of the lesson and is easy to follow for the audience.",
            "numCards": 10,
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

        print(data.get("generationId"))

        while True:
            time.sleep(5)  # Wait for 5 seconds before polling again

            status_response = requests.get(
                f"https://public-api.gamma.app/v1.0/generations/{data.get('generationId')}",
                headers={"X-API-KEY": GammaAPI_KEY}
            )

            if status_response.status_code == 200 and status_response.json().get("status") == "completed":
                with open("presentation.pdf", "wb") as file:
                    file.write(requests.get(status_response.json().get("exportUrl")).content)
                break

            elif status_response.status_code != 200:
                print("Error checking generation status:", status_response.text)
                break
            
            elif status_response.status_code == 200 and timeout > 300:  # Timeout after 5 minutes
                print("Generation is taking too long. Timing out.")
                break

            print("------------------------------")
            print("Generation status:", status_response.json().get("status"))
            print("Status code:", status_response.status_code)
            timeout += 5


        ## Upload presentation to HeyGen and get asset ID to use for video generation of each lesson's presentation video in the video workflow.
        with open("presentation.pdf", "rb") as file:
                    asset_resp = requests.post(
                        "https://api.heygen.com/v3/assets",
                        headers={"X-Api-Key": HeyGenAPI_KEY},
                        files={"file": ("presentation.pdf", file, "application/pdf")}
                    )

        asset_id = asset_resp.json()["data"]["asset_id"]
        print(asset_id)

        vid_prompt_resp = requests.post(
            "https://api.heygen.com/v3/video-agents",
            headers={"X-Api-Key": HeyGenAPI_KEY},
            json={
                "prompt": "Create a video presentation based on the content of the uploaded PDF presentation. The video should be engaging and informative, with visuals that complement the content of the slides. The video should be suitable for educational purposes and should effectively convey the key points of the lesson. Make it fun and engaging to watch for students learning about this topic.",
                "orientation": "landscape",
                "files": [
                    {"type": "asset_id", "asset_id": asset_id}
                ]
            }
        )

        session_id = vid_prompt_resp.json()["data"]["session_id"]
        print(session_id)

        # Step 1: wait for video_id to be assigned
        video_id = None
        while not video_id:
            sess = requests.get(
                f"https://api.heygen.com/v3/video-agents/{session_id}",
                headers={"X-Api-Key": HeyGenAPI_KEY},
            ).json()["data"]
            video_id = sess.get("video_id")
            if not video_id:
                time.sleep(5)

        print(video_id)

        # Step 2: poll video until complete
        while True:
            video = requests.get(
                f"https://api.heygen.com/v3/videos/{video_id}",
                headers={"X-Api-Key": HeyGenAPI_KEY},
            ).json()["data"]
            print(video["status"])
            if video["status"] in ("completed", "failed"):
                break
            time.sleep(10)

        with requests.get(video["video_url"], stream=True) as r:
            r.raise_for_status()
            with open("video.mp4", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        print("Saved to video.mp4")


        quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": user_lesson_prompt + "\n\n" + user_quiz_prompt}]})
        print("Quiz Finished!")
        print("Waiting for 60 seconds before invoking the assignment prompt to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": user_lesson_prompt + "\n\n" + user_assignment_prompt}]})
        print("Assignment Finished!")
        print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
        time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

        print(f"Readings Output for {key}:\n{lesson_output}\n")
        print(f"Quiz Output for {key}:\n{quiz_output}\n")
        print(f"Assignment Output for {key}:\n{assignment_output}\n")