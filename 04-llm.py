from chatlas import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()  # Loads OPENAI_API_KEY from the .env file

with open("prompts/01-system.txt", "r") as f:
    system_prompt = f.read().replace("\n", " ").strip()
system_prompt

chat = ChatOpenAI(
    model="gpt-4o-mini",
    system_prompt=system_prompt,
)

with open("video_transcript.txt", "r") as f:
    video_transcript = f.read().replace("\n", " ").strip()

with open("downloaded_reel/2024-09-16_13-34-25_UTC.txt", "r") as f:
    post_text = f.read().replace("\n", " ").strip()

chat_text = f"""video transcript:

{video_transcript}

post text:

{post_text}
"""

chat.chat(chat_text, stream=False)
