import numpy as np
import pyautogui
import time
import cv2
import pyaudio
import wave
from pynput import keyboard
from threading import Thread
from moviepy.editor import VideoFileClip, AudioFileClip
import os

# Screen recording settings
SCREEN_SIZE = (1920, 1080)
fps = 120
fourcc = cv2.VideoWriter_fourcc(*"XVID")
video_filename = "recorded.avi"
out = cv2.VideoWriter(video_filename, fourcc, 20.0, SCREEN_SIZE)

# Audio recording settings
audio_filename = "recorded_audio.wav"
audio_format = pyaudio.paInt16
channels = 2
rate = 44100
chunk = 1024

# Initialize audio recording
audio = pyaudio.PyAudio()
stream = audio.open(format=audio_format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

frames = []

def record_audio():
    global frames
    while not stop_audio:
        data = stream.read(chunk)
        frames.append(data)

stop_audio = False
audio_thread = Thread(target=record_audio)
audio_thread.start()

# Key press listener
def on_press(key):
    global stop_audio
    try:
        if key.char == 'q':
            stop_audio = True
            return False  # Stop listener
    except AttributeError:
        pass

listener = keyboard.Listener(on_press=on_press)
listener.start()

prev = 0
print("Press 'q' to stop recording.")

while not stop_audio:
    time_elapsed = time.time() - prev
    img = pyautogui.screenshot()

    if time_elapsed > 1.0 / fps:
        prev = time.time()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        out.write(frame)

# Stop recording
listener.join()
stop_audio = True
audio_thread.join()
stream.stop_stream()
stream.close()
audio.terminate()

# Save audio file
with wave.open(audio_filename, 'wb') as wf:
    wf.setnchannels(channels)
    wf.setsampwidth(audio.get_sample_size(audio_format))
    wf.setframerate(rate)
    wf.writeframes(b''.join(frames))

out.release()
print("Recording stopped. Merging video and audio...")


video_clip = VideoFileClip(video_filename)
audio_clip = AudioFileClip(audio_filename)

# Set audio of the video clip to the recorded audio
video_with_audio = video_clip.set_audio(audio_clip)

# Write the result to a new file
output_filename = "recorded.mp4"
video_with_audio.write_videofile(output_filename, codec='libx264', audio_codec='aac')

# Remove intermediate files
os.remove(video_filename)
os.remove(audio_filename)

print(f"Files merged and saved as '{output_filename}'. Intermediate files removed.")
