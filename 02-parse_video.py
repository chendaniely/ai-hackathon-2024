import ffmpeg


def extract_audio_from_video(video_path, audio_path):
    # Use ffmpeg to extract audio
    (
        ffmpeg.input(video_path)
        .output(audio_path, vn=None)  # Exclude video stream
        .run(overwrite_output=True)
    )


# Example usage
video_path = "downloaded_reel/2024-09-16_13-34-25_UTC.mp4"
audio_path = "output_audio.aac"  # Choose .aac, .mp3, or another audio format

extract_audio_from_video(video_path, audio_path)
