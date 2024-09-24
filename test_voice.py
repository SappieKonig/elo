import glob

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio

# voice_samples = load_voice('/Users/kenzoheijman/PycharmProjects/elo2/data/data2')

text = "test this program. Epoch five are the GOATS."

reference_clips = [load_audio(p, 22050) for p in glob.glob('/Users/kenzoheijman/PycharmProjects/elo2/data/data2/*.wav')]
tts = TextToSpeech()
pcm_audio = tts.tts_with_preset(text, voice_samples=reference_clips, preset='fast')

with open('result.wav', 'wb') as f:
    f.write(pcm_audio)
