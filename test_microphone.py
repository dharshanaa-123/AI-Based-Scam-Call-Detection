import sounddevice as sd
from scipy.io.wavfile import write
import os

print("=" * 50)
print("🎤 MICROPHONE TEST")
print("=" * 50)

print()
print("Say this sentence clearly:")
print("Your bank account is blocked. Please give me your OTP immediately.")
print()
print("🎙️ Recording for 5 seconds...")

sample_rate = 16000
duration = 5

os.makedirs("audio", exist_ok=True)

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="int16"
)

sd.wait()

file_path = "audio/fresh_test.wav"
write(file_path, sample_rate, audio)

print()
print("✅ Recording completed.")
print("📁 Saved as:", file_path)
print("=" * 50)