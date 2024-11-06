import whisper

model = whisper.load_model("tiny")
result = model.transcribe("output_audio.aac")
print(result["text"])
