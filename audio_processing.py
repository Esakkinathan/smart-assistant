from gtts import gTTS
import speech_recognition as sr
import ttkbootstrap as ttb
from io import BytesIO
from pydub.playback import play
from pydub import AudioSegment
from threading import Thread
import time
import tkinter as tk


class TextToSpeech:
    def __init__(self, lang="en", tld='co.in', slow=False):
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
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.root = None
        self.label = None
        self.captured_text = None

    def create_ui(self):
        """Create the user interface for speech recognition."""
        try:
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
                text="Hello there,",
                font=('Calibri', 16),
                background='black',
                foreground='white',
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
            return self.captured_text
        except Exception as e:
            print(f"UI Creation Error: {e}")

    def listen(self):
        """
        Listen for audio input with improved error handling.
        """
        try:
            # Indicate that the system is listening
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Set dynamic energy threshold
                self.recognizer.dynamic_energy_threshold = True
                
                # Configure for longer pauses
                self.recognizer.pause_threshold = 3.0
                
                print("Microphone is on, listening...")
                
                # Update UI to show listening state
                self.update_label("Listening...!")
                
                # Listen with standard parameters
                audio = self.recognizer.listen(
                    source, 
                    timeout=10,  # Maximum listening time
                )
                
                print("Audio captured!")
                
                # Process the captured audio
                self.update_label("Processing...!")
                
                # Attempt to recognize speech with multiple recognition attempts
                text = self.recognize_speech(audio)
                
                # Update label with recognized text
                self.update_label(text)
                
                # Store captured text
                self.captured_text = text
                
                return text
        
        except sr.UnknownValueError:
            error_msg = "Sorry, I couldn't understand the audio."
            self.update_label(error_msg)
            #self.captured_text = error_msg
        
        except sr.RequestError as e:
            error_msg = f"Network error: {e}. Please check your internet connection."
            self.update_label(error_msg)
            #self.captured_text = error_msg
        
        except Exception as e:
            error_msg = f"An unexpected error occurred: {e}"
            self.update_label(error_msg)
            #self.captured_text = error_msg
        
        finally:
            # Destroy the UI after 5 seconds
            if self.root:
                self.root.after(5000, self.root.destroy)
            
            return self.captured_text

    def recognize_speech(self, audio):
        """
        Attempt speech recognition with multiple services.
        Provides fallback mechanisms.
        """
        try:
            # Try Google Speech Recognition first
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            try:
                # Fallback to Sphinx (offline recognition)
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except Exception:
                raise sr.UnknownValueError("Could not recognize speech")

    def update_label(self, text):
        """
        Safely update the label text from any thread.
        """
        if self.root and self.label:
            self.root.after(0, self.label.config, {'text': text})

    def on_close(self):
        """
        Properly close the application.
        """
        if self.root:
            self.root.quit()
            self.root.destroy()

# Example usage
if __name__ == "__main__":
    stt = SpeechToText()
    c = stt.create_ui()
    print("Captured Text:", c)
    