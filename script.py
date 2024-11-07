url = "https://www.instagram.com/reel/C_-tH8cPbyO/?utm_source=ig_web_copy_link"
url = "https://www.instagram.com/reel/DAlnO4Rg4UQ/?utm_source=ig_web_copy_link&igsh=MzRlODBiNWFlZA=="  # french
shortcode = get_instagram_shortcode(url)

p_download_base = Path("ig_download")
p_download = p_download_base / shortcode
p_download

download_ig(url, p_download_base)


p_audio = Path("ig_audio") / shortcode
p_audio.mkdir(parents=True)

extract_audio_from_video(
    video_path=list(p_download.glob("*.mp4"))[0]._str,
    audio_path=str(p_audio / "extracted.mp3"),
)

p_trans = Path("ig_trans") / shortcode
p_trans.mkdir(parents=True)

transcribe_audio(
    input_audio_path=p_audio / "extracted.mp3",
    output_text_path=(p_trans / "transcript.txt"),
)

list(p_download.glob("*.txt"))[0]

create_recipe(
    video_text_f=(p_trans / "transcript.txt"),
    post_text_f=(list(p_download.glob("*.txt"))[0]),
    system_f=Path("prompts/01-system.txt"),
)

create_recipe(
    video_text_f=(p_trans / "transcript.txt"),
    post_text_f=(list(p_download.glob("*.txt"))[0]),
    system_f=Path("prompts/02-system_notion.txt"),
)


from notion_client import Client
import os

load_dotenv()

# Initialize the Notion client
notion = Client(auth=os.getenv("NOTION_API_TOKEN"))

# Specify the database ID
database_id = os.getenv(
    "NOTION_DB_ID"
)  # Replace this with your actual database ID

# Insert a new page
new_page = notion.pages.create(
    parent={"database_id": database_id},
    properties={
        "Name": {"title": [{"text": {"content": "Your Page Title"}}]},
        # Add additional properties here as needed
        "Status": {"select": {"name": "In Progress"}},
    },
)

print("New page created with ID:", new_page["id"])
