# AI Canvas Course Generator

This project uses AI agents to generate a full course package for an HCI course. It can create lesson readings, quizzes, assignments, answer keys, presentations, and video/audio assets from prompts stored in the repository.

## What this project does

The main workflow is driven by [AiAgent.py](AiAgent.py). It:

- reads the course prompts from [prompts.json](prompts.json)
- loads agent instructions from [system_prompts](system_prompts)
- generates HTML lesson content, quizzes, assignments, and syllabus materials
- calls external services for presentations and audio/video generation
- writes outputs into the [deliverables](deliverables) folder

## Prerequisites

Before running the project, make sure you have the following installed and available:

- Python 3.10+ (3.11 recommended)
- Node.js 20+ with npm
- Docker Desktop installed and running
- A Google AI Studio account and API key for Gemini
- A Gamma API key for presentation generation
- The OpenCode CLI installed and available on your PATH as `opencode.cmd`
- Internet access for API calls to Google, Gamma, and the TTS service

> The scripts in this repository use Windows-style command files such as `opencode.cmd`, `npx.cmd`, and `npm.cmd`. This project is intended for a Windows development environment.

## Project structure

- [AiAgent.py](AiAgent.py) - main automated course-generation script
- [Chatbot.py](Chatbot.py) - interactive chatbot-oriented workflow
- [prompts.json](prompts.json) - lesson and assignment prompts for the course
- [system_prompts](system_prompts) - system instructions used by the agents
- [deliverables](deliverables) - generated course files
- [requirements.txt](requirements.txt) - Python dependencies
- [package.json](package.json) - Node dependencies used by the video workflow

## 1. Clone and open the repository

```powershell
git clone https://github.com/ATenorSaxophone/AI-Course-Generator
cd "AI Canvas Course Generator"
```

## 2. Create a Python virtual environment

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
```

## 3. Install Python dependencies

```powershell
pip install -r requirements.txt
```

## 4. Install Node dependencies

```powershell
npm install
```

## 5. Create a `.env` file

Create a file named `.env` in the project root and add the required environment variables:

```env
MY_GAMMA_KEY=your_gamma_api_key
MY_GOOGLE_KEY=your_google_api_key
MY_GOOGLE_KEY_LESSONS=your_google_api_key_for_lessons
MY_GOOGLE_KEY_QUIZZES=your_google_api_key_for_quizzes
MY_GOOGLE_KEY_ANS_KEY=your_google_api_key_for_answer_keys
MY_GOOGLE_KEY_ASSIGNMENTS=your_google_api_key_for_assignments
MY_GOOGLE_KEY_ASSIGNMENTS_KEY=your_google_api_key_for_assignment_keys
```

If you are using a different setup, make sure the environment variable names match what the Python scripts expect.

## 6. Start the Kokoro text-to-speech service

The audio workflow expects a local Kokoro-compatible API server on port 8880.

```powershell
docker rm -f kokoro-tts-cpu 2>$null

docker run -d -p 8880:8880 --name kokoro-tts-cpu ghcr.io/remsky/kokoro-fastapi-cpu:v0.2.2
```

Verify that the container is running:

```powershell
docker ps
```

## 7. Run the generator

To generate the full course package, run:

```powershell
python AiAgent.py
```

This may take a long time because it is calling AI services and creating media assets. The generated files will appear under the [deliverables](deliverables) folder.

## 8. Run the chatbot workflow (optional)

If you want to use the interactive chatbot-style workflow instead of the full automated generation script, run:

```powershell
python Chatbot.py
```

## Customizing prompts

You can change the course content by editing [prompts.json](prompts.json). The agent behavior can also be changed by modifying the markdown files in [system_prompts](system_prompts).

## Troubleshooting

- If you see `ModuleNotFoundError`, activate the virtual environment again and reinstall dependencies.
- If Docker fails, make sure Docker Desktop is running and that the daemon is available.
- If the scripts cannot find `opencode.cmd`, install the OpenCode CLI and ensure it is on your PATH.
- If API calls fail, double-check your `.env` values and your internet connection.
- If video rendering fails, make sure Node dependencies were installed successfully and that your environment can run the Remotion toolchain.

## Notes

- The full generation pipeline can be lengthy, especially when creating audio and video outputs.
- The repository is designed for a Windows machine and uses Windows shell commands in several places.
- Some generated assets may be large and can take significant disk space, especially in the [deliverables](deliverables) folder.
