from gtts import gTTS
import gtts
import speech_recognition as sr
import ttkbootstrap as ttb
from io import BytesIO
from pydub.playback import play
from pydub import AudioSegment
from threading import Thread
import requests
import pyaudio
from function_tools import wifi_handler,MessageWindow
import numpy as np
import noisereduce as nr
import scipy.io.wavfile as wav

class TextToSpeech:
    def __init__(self, lang="en", tld='co.in', slow=False):
        self.lang = lang
        self.tld = tld
        self.slow = slow
        self.win = MessageWindow()

    def speak(self, text):
        try:
            mp3_fp = BytesIO()
            tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=self.slow)
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            sound = AudioSegment.from_file(mp3_fp, format="mp3")
            play(sound)
        except gtts.tts.gTTSError:
            wifi_handler()
            self.speak(text)
        except requests.ConnectionError:
            return 2
        except requests.Timeout:
            self.win.send_message(message="Connection timed out.\n The assistant will be stopped.\nPlease try again later.")
            exit()
        except Exception as e:
            self.win.send_message(message="An error Occured.\n Please try again later.")
            exit()                

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.root = None
        self.label = None
        self.captured_text = None
        self.e_flag = False

    def check_microphone(self):
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        for i in range(device_count):
            device_info = p.get_device_info_by_index(i)
            if device_info["maxInputChannels"] > 0: 
                return True
        return False

    def create_ui(self):
        try:
            self.root = ttb.Window(themename="cyborg")
            self.root.title("DARLA")
            self.root.geometry("400x250")
            self.root.attributes('-topmost', True)
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            x = (screen_width - 400) // 2
            y = (screen_height - 250) // 2
            self.root.geometry(f"400x250+{x}+{y}")
            self.label = ttb.Label(
                self.root,
                text="Hello there,",
                font=('Calibri', 16),
                background='black',
                foreground='white',
                wraplength=380,
                anchor='center',
                justify='center'
            )
            self.label.pack(expand=True, padx=10, pady=10)
            listen_thread = Thread(target=self.listen, daemon=True)
            listen_thread.start()
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.root.mainloop()
            if self.e_flag:
                self.e_flag=False
                wifi_handler()
                self.create_ui()
            return self.captured_text
        except Exception as e:
            print(f"UI Creation Error: {e}")

    def listen(self):
        e_flag=False
        try:
            if not self.check_microphone():
                self.label.config(text = "No Microphone detected")
                self.root.after(5000, self.on_close)
                exit()
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
                self.recognizer.dynamic_energy_threshold = True
                self.recognizer.pause_threshold = 3.0
                print("Microphone is on, listening...")
                self.label.config(text = "Listening...!")
                audio = self.recognizer.listen(source,timeout=10,phrase_time_limit=10)
                #play(audio)
                print("Audio captured!")
                self.label.config(text = "Processing...!")
                #sample_rate = audio.sample_rate  # You can adjust this based on your microphone's sampling rate
                #audio_data = np.frombuffer(audio.frame_data, dtype=np.int16)

                # Apply noise reduction
                #reduced_noise_audio = nr.reduce_noise(y=audio_data, sr=sample_rate)
                #cleaned_audio = sr.AudioData(reduced_noise_audio.tobytes(), sample_rate, 2)
                text = self.recognize_speech(audio)
                self.label.config(text = text)
                self.captured_text = text
                return text
            
        except sr.UnknownValueError:
            self.label.config(text = "Sorry, I couldn't understand the audio.")
        except sr.RequestError as e:
            self.e_flag= True
            self.label.config(text = f"Network error: \nPlease check your internet connection.\n Assistant exits")
        except sr.WaitTimeoutError as e:
            self.label.config(text = 'Time exceeds, Are you there?')
        except Exception as e:
            self.label.config(text = f"An unexpected error occurred: {e}")
            
        finally:
            if self.root:
                self.root.after(5000, self.on_close)
            return self.captured_text

    def recognize_speech(self, audio):
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except Exception:
                raise sr.UnknownValueError("Could not recognize speech")
    def on_close(self):
        if self.root:
            self.root.destroy()
            self.root = None
            self.label = None

