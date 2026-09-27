import whisper

print("=" * 50)
print("🎤 WHISPER SPEECH RECOGNITION TEST")
print("=" * 50)

print("🔄 Loading Whisper model...")
model = whisper.load_model("small")

print("🎧 Reading audio...")

result = model.transcribe(
    "audio/fresh_test.wav",
    language="en",
    fp16=False,
    temperature=0,
    condition_on_previous_text=False
)

text = result["text"].strip()

print()
print("✅ TRANSCRIPTION RESULT:")
print(text)

print("=" * 50)