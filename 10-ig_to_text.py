from pathlib import Path
import re
from urllib.parse import urlparse
import os

import instaloader
import ffmpeg
import whisper
from notion_client import Client
from chatlas import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# https://www.instagram.com/reel/C_-tH8cPbyO/?utm_source=ig_web_copy_link


def get_instagram_shortcode(url):
    # Remove tracking parameters if any
    parsed_url = urlparse(url)
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    # Regex pattern to match Instagram shortcode
    pattern = r"(?:instagram\.com/(?:p|reel)/)([A-Za-z0-9_-]+)"

    match = re.search(pattern, clean_url)
    if match:
        return match.group(1)  # Return the shortcode
    else:
        raise UserWarning("No shortcode found.")
        return None  # No shortcode found


# Example usage:
url = "https://www.instagram.com/p/CTgUAKNJdZZ/?utm_source=ig_web_copy_link"
shortcode = get_instagram_shortcode(url)
assert shortcode == "CTgUAKNJdZZ"

url = "https://www.instagram.com/reel/C_-tH8cPbyO/?utm_source=ig_web_copy_link"
shortcode = get_instagram_shortcode(url)
assert shortcode == "C_-tH8cPbyO"


def download_ig(reel_url: str, download_dir_base: str) -> None:
    """Downloads instagram post to directory, returns the ig slug"""

    L = instaloader.Instaloader()
    shortcode = get_instagram_shortcode(reel_url)

    p = Path(download_dir_base) / shortcode
    if not p.exists():
        p.mkdir(parents=True)

    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target=p)

    return None


def extract_audio_from_video(
    video_path: str | Path, audio_path: str | Path
) -> Path:
    # Use ffmpeg to extract audio
    (
        ffmpeg.input(video_path)
        .output(
            audio_path,
            vn=None,  # Exclude video stream
            loglevel="error",
            **{
                # Use 64k bitrate for smaller file
                "b:a": "64k",
                # Only output one channel, again for smaller file
                "ac": "1",
            },
        )
        .run(overwrite_output=True)
    )


def detect_language():
    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)


def transcribe_audio(
    input_audio_path: str | Path,
    output_text_path: str | Path,
    model: str = "tiny",
) -> None:
    """ """
    model = whisper.load_model(model)

    audio = whisper.load_audio(input_audio_path)
    audio = whisper.pad_or_trim(audio)

    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")

    # decode the audio
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    # print the recognized text
    print(result.text)

    with open(output_text_path, "w") as f:
        print(output_text_path)
        f.write(result.text)


def create_recipe(video_text_f, post_text_f, system_f):
    with open(system_f, "r") as f:
        system_prompt = f.read().replace("\n", " ").strip()
    system_prompt

    chat = ChatOpenAI(
        model="gpt-4o-mini",
        system_prompt=system_prompt,
    )

    with open(video_text_f, "r") as f:
        video_transcript = f.read().replace("\n", " ").strip()

    with open(post_text_f, "r") as f:
        post_text = f.read().replace("\n", " ").strip()

    chat_text = f"""video transcript:

    {video_transcript}

    post text:

    {post_text}
    """

    text = chat.chat(chat_text, stream=False)
    return text
