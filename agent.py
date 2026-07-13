# Agent AI that creates Canvas Class about Human-Computer Interaction (HCI) using LangChain and Anthropic's Claude API. The agent will use the FastMCP server to create a Canvas Class with the specified parameters.
import base64
import json
import os

from dotenv import load_dotenv
import time, requests

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.agents.middleware import ModelRetryMiddleware

from google import genai
from openai import OpenAI

# Get .env variables
load_dotenv()
google_key = os.getenv("MY_GOOGLE_KEY")
HeyGenAPI_KEY = os.getenv("MY_HEYGEN_KEY")
GammaAPI_KEY = os.getenv("MY_GAMMA_KEY")

#Create Google AI Studio model
google_gemini_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.environ["MY_GOOGLE_KEY"],
    temperature=0.1
)

google_audio_model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-live-preview",
    api_key=os.environ["MY_GOOGLE_KEY_2"],
    temperature=0.1
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

google_prompt_agent = create_agent(
    model=google_gemini_model,
    tools=[search_tool],
    system_prompt=video_prompt
)

google_audio_agent = create_agent(
    model=google_audio_model,
    tools=[search_tool],
    system_prompt=video_prompt,
    middleware=[
        ModelRetryMiddleware(
            max_retries=0
        )
    ]
)

#get prompts from prompts.json file
with open("prompts.json", "r", encoding="utf-8") as file:
    prompts = json.load(file)


# Run agent with prompt inputs and print outputs
# for key, value in prompts.items():

#     if key == "lesson 15":
#         final_project_prompt = prompts["lesson 15"]["final presentation prompt"]

#         final_project_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": final_project_prompt}]})
#         with open("deliverables/lesson 15/final_project.html", "w", encoding="utf-8") as file:
#             file.write(final_project_output["messages"][1].content[0]["text"])

#         print("Final Project Finished!")
#         print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
#         time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

#     elif key == "lesson 16":
#         final_exam_prompt = value["final exam prompt"]
#         lesson_content = ""

#         for lesson_num in range(1, 15):
#             with open(f"deliverables/{f"lesson {lesson_num}"}/{f"lesson {lesson_num}"}_lesson.html", "r", encoding="utf-8") as file:
#                 lesson_content += "\n\n" + file.read()
#                 print(f"Lesson {lesson_num} file read!")

#         final_exam_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Content: {lesson_content} \n\n Prompt: {final_exam_prompt}"}]})

#         with open("deliverables/lesson 16/final_exam.html", "w", encoding="utf-8") as file:
#             file.write(final_exam_output["messages"][1].content[0]["text"])

#         print("Final Exam Finished!")
#         print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
#         time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

#     else:
#         user_lesson_prompt = value["lesson prompt"]
#         user_quiz_prompt = value["quiz prompt"]
#         user_assignment_prompt = value["assignment prompt"]

#         # Run the agent with the combined prompt
#         lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": user_lesson_prompt}]})
#         with open(f"{key}_lesson.html", "w", encoding="utf-8") as file:
#             file.write(lesson_output["messages"][1].content[0]["text"])
#         print("Lesson Finished!")
#         print("Waiting for 60 seconds before invoking the quiz and assignment prompts to avoid hitting rate limits...")
#         time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

#         #Create presentation for the lesson using the presentation agent and the user_lesson_prompt as the base content for the presentation.
#         response = requests.post(
#             "https://public-api.gamma.app/v1.0/generations",
#             headers={"X-API-KEY": GammaAPI_KEY, "Content-Type": "application/json"},
#             data=json.dumps({
#             "textMode": "generate",
#             "format": "presentation",
#             "cardSplit": "auto",
#             "exportAs": "pdf",
#             "inputText": lesson_output["messages"][1].content[0]["text"],
#             "additionalInstructions": "Make it visually engaging and informative, with a professional design suitable for marketing executives. Use relevant visuals and graphics to complement the content of the slides. Add speaker notes for each slide that provide additional context and information for the presenter. Ensure that the presentation effectively conveys the key points of the lesson and is easy to follow for the audience.",
#             "numCards": 10,
#             "themeId": "electric",
#             "textOptions": {
#                 "amount": "detailed",
#                 "language": "en",
#                 "tone": "professional",
#                 "audience": "college students"
#             },
#             "imageOptions": {
#                 "model": "flux-2-pro",
#                 "source": "aiGenerated",
#                 "style": "photorealistic, professional"
#             },
#             "cardOptions": {
#                 "dimensions": "16x9",
#             },
#             "sharingOptions": {
#                 "workspaceAccess": "view",
#                 "externalAccess": "noAccess"
#             },
#             })
#         )

#         data = response.json()
#         print(data)
#         timeout = 0

#         print(data.get("generationId"))

#         while True:
#             time.sleep(5)  # Wait for 5 seconds before polling again

#             status_response = requests.get(
#                 f"https://public-api.gamma.app/v1.0/generations/{data.get('generationId')}",
#                 headers={"X-API-KEY": GammaAPI_KEY}
#             )

#             if status_response.status_code == 200 and status_response.json().get("status") == "completed":
#                 with open("presentation.pdf", "wb") as file:
#                     file.write(requests.get(status_response.json().get("exportUrl")).content)
#                 break

#             elif status_response.status_code != 200:
#                 print("Error checking generation status:", status_response.text)
#                 break
            
#             elif status_response.status_code == 200 and timeout > 300:  # Timeout after 5 minutes
#                 print("Generation is taking too long. Timing out.")
#                 break

#             print("------------------------------")
#             print("Generation status:", status_response.json().get("status"))
#             print("Status code:", status_response.status_code)
#             timeout += 5

#         if key != "lesson 8":
#             quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": lesson_output + "\n\n" + user_quiz_prompt}]})
#             print("Quiz Finished!")
#             print("Waiting for 60 seconds before invoking the assignment prompt to avoid hitting rate limits...")
#             time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

#         else:
#             for lesson_num in range(1, 9):
#                 with open(f"deliverables/{"lesson {lesson_num}"}_lesson.html", "r", encoding="utf-8") as file:
#                     lesson_content += "\n\n" + file.read()

#             quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"{lesson_output}\n\n{lesson_content}\n\nPrompt: {user_quiz_prompt}"}]})
#             with open(f"deliverables/{"lesson 8"}/{"lesson 8"}_quiz_iterated.html", "w", encoding="utf-8") as file:
#                 file.write(quiz_output["messages"][1].content[0]["text"])
#             print("Quiz Finished!")
#             print("Waiting for 60 seconds before invoking the assignment prompt to avoid hitting rate limits...")

#         assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": lesson_output + "\n\n" + user_assignment_prompt}]})
#         print("Assignment Finished!")
#         print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
#         time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

#     lesson_content = ""
#     assignment_content = ""

#     for lesson_num in range(1,15):
#         with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_lesson.html", "r", encoding="utf-8") as file:
#             lesson_content += f"\n\n{file.read()}"
#             print(f"read file lesson {lesson_num}")
        
#         if(lesson_num > 5):
#             with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_assignment.html", "r", encoding="utf-8") as file:
#                 assignment_content += f"\n\n{file.read()}"
#                 print(f"read file assignment {lesson_num}")
        
#         else:
#             with open(f"deliverables/lesson {lesson_num}/Iterated/lesson {lesson_num}_assignment.html", "r", encoding="utf-8") as file:
#                 assignment_content += f"\n\n{file.read()}"
#                 print(f"read file assignment {lesson_num}")

#     syllabus_output = google_syllabus_agent.invoke({"messages": [{"role": "user", "content": f"{assignment_content}\n{prompts["syllabus"]}"}]})
#     with open(f"deliverables/syllabus/syllabus.html", "w", encoding="utf-8") as file:
#         file.write(syllabus_output["messages"][1].content[0]["text"])
#     print("Syllabus finished")
#     print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
#     time.sleep(60) # Add a short delay between calls to avoid hitting rate limits

#     # Creates a Agreement form for the first lesson, as the assignment requires a syllabus agreement form to be "signed".
#     syllabus = ""

#     with open("deliverables/syllabus/syllabus.html", "r", encoding="utf-8") as file:
#         syllabus = file.read()

#     syllabus_quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Syllabus: {syllabus}\n\n{prompts["syllabus"]["agreement form"]}"}]})
#     with open("deliverables/syllabus/syllabus_agreement_form.html", "w", encoding="utf-8") as file:
#         file.write(syllabus_quiz_output["messages"][1].content[0]["text"])
#     print("Agreement form finished!")
#     print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
#     time.sleep(60) # Add a short delay between calls to avoid hitting rate limits

#     print(f"Readings Output for {key}:\n{lesson_output}\n")
#     print(f"Quiz Output for {key}:\n{quiz_output}\n")
#     print(f"Assignment Output for {key}:\n{assignment_output}\n")






# lesson_output = google_lesson_agent.invoke({"messages": [{"role": "user", "content": prompts["lesson 10"]["lesson prompt"]}]})
# with open(f"deliverables/{"lesson 10"}/{"lesson 10"}_lesson.html", "w", encoding="utf-8") as file:
#     file.write(lesson_output["messages"][1].content[0]["text"])
# print("Lesson Finished!")
# print("Waiting for 60 seconds before invoking the quiz and assignment prompts to avoid hitting rate limits...")
# time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

# Create presentation for the lesson using the presentation agent and the user_lesson_prompt as the base content for the presentation.
# response = requests.post(
#     "https://public-api.gamma.app/v1.0/generations",
#     headers={"X-API-KEY": GammaAPI_KEY, "Content-Type": "application/json"},
#     data=json.dumps({
#     "textMode": "generate",
#     "format": "presentation",
#     "cardSplit": "auto",
#     "exportAs": "pdf",
#     "inputText": lesson_output["messages"][1].content[0]["text"],
#     "additionalInstructions": presentation_prompt,
#     "numCards": 13,
#     "themeId": "electric",
#     "textOptions": {
#         "amount": "detailed",
#         "language": "en",
#         "tone": "professional",
#         "audience": "college students"
#     },
#     "imageOptions": {
#         "model": "flux-2-pro",
#         "source": "aiGenerated",
#         "style": "photorealistic, professional"
#     },
#     "cardOptions": {
#         "dimensions": "16x9",
#     },
#     "sharingOptions": {
#         "workspaceAccess": "view",
#         "externalAccess": "noAccess"
#     },
#     })
# )

# data = response.json()
# print(data)
# timeout = 0
# x=1

# print(data.get("generationId"))

# while True:
#     time.sleep(5)  # Wait for 5 seconds before polling again

#     status_response = requests.get(
#         f"https://public-api.gamma.app/v1.0/generations/{data.get('generationId')}",
#         headers={"X-API-KEY": GammaAPI_KEY}
#     )

#     if status_response.status_code == 200 and status_response.json().get("status") == "completed":
#         with open(f"deliverables/{"lesson 1"}/{"lesson 1"}_presentation.pdf", "wb") as file:
#             file.write(requests.get(status_response.json().get("exportUrl")).content)
#         break

#     elif status_response.status_code != 200:
#         print("Error checking generation status:", status_response.text)
#         break
    
#     elif status_response.status_code == 200 and timeout > 300:  # Timeout after 5 minutes
#         print("Generation is taking too long. Timing out.")
#         break

#     print(f"-----------------------------{x}")
#     print("Generation status:", status_response.json().get("status"))
#     print("Status code:", status_response.status_code)
#     x += 1
#     timeout += 5

# with open(f"deliverables/lesson 9/lesson 9_lesson.html", "r", encoding="utf-8") as file:
#     lesson_output = f"\n\n {file.read()}"

# lesson_output = ""

# with open(f"deliverables/lesson 4/lesson 4_lesson.html", "r", encoding="utf-8") as file:
#     lesson_output = file.read()
#     print("read lesson 4!")

# quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"{lesson_output["messages"][1].content[0]["text"]} \n\n {prompts['lesson 9']['quiz prompt']}"}]})
# with open(f"deliverables/{"lesson 9"}/{"lesson 9"}_quiz.html", "w", encoding="utf-8") as file:
#     file.write(quiz_output["messages"][1].content[0]["text"])
# print("Quiz Finished!")
# print("Waiting for 60 seconds before invoking the assignment prompt to avoid hitting rate limits...")
# time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits

# assignment_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"{lesson_output} \n\n {prompts['lesson 4']['assignment prompt']}"}]})
# with open(f"deliverables/{"lesson 4"}/{"lesson 4"}_assignment.html", "w", encoding="utf-8") as file:
#     file.write(assignment_output["messages"][1].content[0]["text"])
# print("Assignment Finished!")
# print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
# time.sleep(60)  # Add a short delay between calls to avoid hitting rate limits



# # Creates a syllabus using the assignments generated from each lesson. This allows the AI to get enough information to see what each week is about, as well as create a timeline for when each assignment is due when.
# lesson_content = ""
# assignment_content = ""

# for lesson_num in range(1,15):
#     # with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_lesson.html", "r", encoding="utf-8") as file:
#     #     lesson_content += f"\n\n{file.read()}"
#     #     print(f"read file lesson {lesson_num}")
    
#     if(lesson_num > 5):
#         with open(f"deliverables/lesson {lesson_num}/lesson {lesson_num}_assignment.html", "r", encoding="utf-8") as file:
#             assignment_content += f"\n\n{file.read()}"
#             print(f"read file assignment {lesson_num}")
    
#     else:
#         with open(f"deliverables/lesson {lesson_num}/Iterated/lesson {lesson_num}_assignment.html", "r", encoding="utf-8") as file:
#             assignment_content += f"\n\n{file.read()}"
#             print(f"read file assignment {lesson_num}")

# syllabus_output = google_syllabus_agent.invoke({"messages": [{"role": "user", "content": f"{assignment_content}\n{prompts["syllabus"]}"}]})
# with open(f"deliverables/syllabus/syllabus.html", "w", encoding="utf-8") as file:
#     file.write(syllabus_output["messages"][1].content[0]["text"])
# print("Syllabus finished")
# print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
# time.sleep(60) # Add a short delay between calls to avoid hitting rate limits


# # Creates a Agreement form for the first lesson, as the assignment requires a syllabus agreement form to be "signed".
# syllabus = ""

# with open("deliverables/syllabus/syllabus.html", "r", encoding="utf-8") as file:
#     syllabus = file.read()

# # Creates a quiz that works as a syllabus agreement form
# syllabus_quiz_output = google_quiz_assignment_agent.invoke({"messages": [{"role": "user", "content": f"Syllabus: {syllabus}\n\n{prompts["syllabus"]["agreement form"]}"}]})
# with open("deliverables/syllabus/syllabus_agreement_form.html", "w", encoding="utf-8") as file:
#     file.write(syllabus_quiz_output["messages"][1].content[0]["text"])
# print("Agreement form finished!")
# print("Waiting for 60 seconds before moving on to the next lesson to avoid hitting rate limits...")
# time.sleep(60) # Add a short delay between calls to avoid hitting rate limits

# client = genai.Client(api_key=os.environ["MY_GOOGLE_KEY_2"])
# print(f"client key: ", f"api_key: {os.environ['MY_GOOGLE_KEY']}")

# myfile = client.files.upload(file="deliverables/lesson 1/lesson 1_presentation.pdf")

# interaction = client.interactions.create(
#     model="gemini-2.5-flash",
#     input=[
#         {"type": "text", "text": "Create an audio prompt of the following presentation. Do not provide instructions, only words that are to be spoken. Try to make the script long enough to cover 20 minutes of audio. Do not include any other characters other than letters and punctuation."},
#         {"type": "document", "uri": myfile.uri, "mime_type": myfile.mime_type}
#     ]
# )

# client.files.delete(name=myfile.name)

# client = OpenAI(
#     base_url="http://localhost:8880/v1", api_key="not-needed"
# )

# with client.audio.speech.with_streaming_response.create(
#     model="kokoro",
#     voice="af_sky+af_bella", #single or multiple voicepack combo
#     input= interaction.output_text
#     ) as response:
#       response.stream_to_file("output.mp3")


