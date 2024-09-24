import torch
import glob
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio
from scipy.io.wavfile import write
import numpy as np

text = "test this program. Epoch five are the GOATS."

reference_clips = [load_audio(p, 22050) for p in glob.glob('data/*.wav')]
tts = TextToSpeech()

# Generate PCM audio
pcm_audio = tts.tts_with_preset(text, voice_samples=reference_clips, preset='fast')

# Convert the tensor to numpy array
pcm_audio_np = pcm_audio.cpu().numpy()

# Scale the tensor values to int16 if they are in float32 range (-1, 1)
scaled_audio = np.int16(pcm_audio_np / np.max(np.abs(pcm_audio_np)) * 32767)

# Define the sample rate (make sure it matches what Tortoise is generating)
sample_rate = 22050  # Assuming 22.05kHz, adjust if needed

# Save as a .wav file
write('result.wav', sample_rate, scaled_audio)

print("WAV file saved as result.wav")
