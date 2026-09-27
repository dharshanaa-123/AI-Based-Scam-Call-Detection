import whisper

print("Loading Whisper model...")
model = whisper.load_model("small")

def transcribe_audio(file_path):
    print("🎧 Transcribing audio...")

    result = model.transcribe(
        file_path,
        language="en",
        fp16=False,
        temperature=0,
        condition_on_previous_text=False
    )

    text = result["text"].strip()

    print("📝 Transcription:")
    print(text)

    return text