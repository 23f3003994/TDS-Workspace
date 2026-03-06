from faster_whisper import WhisperModel

model = WhisperModel("small")

segments, info = model.transcribe("segment.mp3", language="en")

for segment in segments:
    print(segment.text)