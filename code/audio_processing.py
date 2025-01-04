from gtts import gTTS
import speech_recognition as sr
import ttkbootstrap as ttb
from io import BytesIO
from pydub.playback import play
from pydub import AudioSegment
from threading import Thread


class TextToSpeech:
    def _init_(self, lang="en", tld='co.in', slow=False):
        self.lang = lang
        self.tld = tld
        self.slow = slow

    def speak(self, text):
        mp3_fp = BytesIO()
        tts = gTTS(text=text, lang=self.lang, tld=self.tld, slow=self.slow)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        sound = AudioSegment.from_file(mp3_fp, format="mp3")
        play(sound)

class SpeechToText:
    def _init_(self):
        self.recognizer = sr.Recognizer()
        self.root = None
        self.label = None

    def create_ui(self):
        # Create the UI
        self.root = ttb.Window(themename="cyborg")
        self.root.title("DARLA")
        self.root.geometry("400x250")
        self.root.attributes('-topmost', True)

        # Center the window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - 400) // 2
        y = (screen_height - 250) // 2
        self.root.geometry(f"400x250+{x}+{y}")

        # Configure the label
        self.label = ttb.Label(
            self.root,
            text="Listening...!",
            font=('Calibri', 16),
            background='black',
            wraplength=380,
            anchor='center',
            justify='center'
        )
        self.label.pack(expand=True, padx=10, pady=10)

        # Start listening in a new thread
        listen_thread = Thread(target=self.listen, daemon=True)
        listen_thread.start()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def listen(self):
        try:
            # Indicate that the system is listening
            self.label.config(text="Listening...!")

            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source)
                print("Microphone is on, listening...")
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)
                print("Audio captured!")

                # Process the captured audio
                self.label.config(text="Processing...!")
                text = self.recognizer.recognize_google(audio)
                self.label.config(text=text)

        except sr.UnknownValueError:
            text = "Sorry, I couldn't understand the audio."
            self.label.config(text="Sorry, I couldn't understand the audio.")
        except sr.RequestError as e:
            text = f"Request error: {e}"
            self.label.config(text=text)
        except Exception as e:
            text=f"An error occurred: {e}"
            self.label.config(text=text)
        finally:
            # Destroy the UI after 5 seconds
            return text
            self.root.after(5000, self.root.destroy)

    def on_close(self):
        # Close the application
        self.root.destroy()

