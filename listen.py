import pyaudio
import whisper
import numpy as np
import tempfile
import wave
import torch
import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
# Load the Whisper model specifically for English
model = whisper.load_model("small.en")  # Use the English-only model

# Load the Silero VAD model from Torch Hub
vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad')
(get_speech_timestamps, _, read_audio, _, _) = utils

# Audio configuration
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 512  # Set chunk size to 512 for 16kHz
SILENCE_TIMEOUT = 5  # Time in seconds to wait for silence

def listen():
    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    root = ttk.Window(themename="cyborg")
    root.title('DARLA')
    root.geometry('500x100')
    # Start streaming audio
    label = ttk.Label(root,text="Listening...!", font=("Aerial",16))
    label.pack(pady=20)
    print("Recording... Speak now! (Silence for 5 seconds will stop the recording)")

    try:
        frames = []
        is_speaking = False
        silence_start_time = None

        while True:
            # Collect audio data
            data = stream.read(CHUNK)
            frames.append(data)

            # Convert audio data to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0  # Normalize to [-1.0, 1.0]

            # Check for voice activity
            speech_probabilities = vad_model(torch.tensor(audio_data).unsqueeze(0), sr=RATE)  # Pass the sample rate
            if speech_probabilities[0] > 0.5:  # Adjust threshold as needed
                is_speaking = True
                silence_start_time = None  # Reset silence timer
            else:
                if is_speaking:
                    # If we were speaking and now we are not, start the silence timer
                    if silence_start_time is None:
                        silence_start_time = time.time()
                    elif time.time() - silence_start_time > SILENCE_TIMEOUT:
                        # If silence has lasted longer than the timeout, break the loop
                        print("Silence detected for 5 seconds. Finalizing input...")
                        break
        label.config(text="Processing...")
        label.update()
        # Save the audio data to a temporary file
        with tempfile.NamedTemporaryFile(delete=True, suffix='.wav') as tmpfile:
            with wave.open(tmpfile.name, 'wb') as wav_file:
                wav_file.setnchannels(CHANNELS)
                wav_file.setsampwidth(audio.get_sample_size(FORMAT))
                wav_file.setframerate(RATE)
                wav_file.writeframes(b''.join(frames))

            # Load the audio file for transcription
            audio_data = whisper.load_audio(tmpfile.name)
            audio_data = whisper.pad_or_trim(audio_data)

            # Transcribe the audio data
            result = model.transcribe(audio_data, language="en")  # Specify language as English
            transcribed_text = result['text']
            label.config(text=transcribed_text)
            label.update()
            time.sleep(5)
            root.destroy()
            return transcribed_text.strip()  # Return the transcribed text

    except KeyboardInterrupt:
        print("\nRecording stopped.")
        return None

    finally:
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        audio.terminate()

print(listen())

