
import pvporcupine
from pvrecorder import PvRecorder
import threading
import re
import random
from audio_processing import TextToSpeech, SpeechToText
from model_processing import ModelProcessor
from action_processing import ActionProcessor
import sys
import time
import queue

ACCESS_KEY = "J120zHFuE4BpX3MgE9LK1XrADoYoUhH+ornTxInbKT5YT9eKHsUqcg=="  # Replace with your API key
WAKEWORD_PATH = r"hey-darla/hey-darla.ppn"
EXIT_PATH = r"hey-darla/stop-darla.ppn"

class Darla:
    def __init__(self,audio):
        self.stt = SpeechToText()
        self.tts = TextToSpeech()
        self.action = ActionProcessor(audio=audio)
        self.model = ModelProcessor()
        self.is_running = True  # Assistant starts in active mode
        self.is_response = False
        self.user_query = ""
        self.output_text = ""
        self.text_to_speak = ""
        self.exit_flag = False  # New flag to control application exit
        if audio:
            self.queue = queue.Queue()  
            # Wake word detection setup
            self.porcupine = pvporcupine.create(
                access_key=ACCESS_KEY, 
                keyword_paths=[WAKEWORD_PATH, EXIT_PATH]
            )
            self.recorder = PvRecorder(frame_length=self.porcupine.frame_length, device_index=-1)

            # Start wake word detection in a separate thread
            self.wake_thread = threading.Thread(target=self.listen_for_wake_word, daemon=True)
            self.wake_thread.start()

    def get_random_variation(self, category):
        """Selects a random variation for responses."""
        variations = {
            "greeting": [
                "What can I do for you?",
                "How can I assist you today?",
                "What can I help you with?",
                "How may I help you?",
                "Is there something I can do for you?",
                "What can I help you out with?",
                "What do you need help with?",
                "How can I be of service?",
                "What task would you like me to perform?",
                "What would you like me to do?"
            ],
            "understanding": [
                "I couldn't understand. Please try again.",
                "Sorry, I didn't get that. Can you say it again?",
                "I'm having trouble understanding. Could you repeat that?",
                "I didn't catch that. Could you please say it again?",
                "I'm sorry, I didn't quite hear that. Can you repeat it?",
                "Could you please rephrase? I couldn't understand.",
                "Sorry, I didn't understand. Can you say it again?",
                "I wasn't able to understand that. Please try again.",
                "Can you say that again? I didn't quite get it.",
                "Please try again, I couldn't understand."
            ],
            "exit": [
                "I'm signing off now. Have a wonderful day!",
                "That's it for now! Take care and have a great day ahead!",
                "Shutting down. Wishing you a fantastic day!",
                "I'm going offline. Stay safe and have an amazing day!",
                "Time for me to rest. Enjoy your day to the fullest!",
                "Exiting now. Hope you have a productive and joyful day!",
                "Goodbye for now! Have a nice day ahead!",
                "I'm powering down. Wishing you a peaceful and happy day!",
                "Logging off. Take it easy and have a great day!",
                "I'm going quiet now. Have a good day and see you soon!"
            ],
            "standby": [
                "Okay, going to standby mode. Call me if you need anything.",
                "Entering standby mode now. If you need anything, just call me.",
                "I'm going to standby mode now. Reach out if you need anything.",
                "Okay, I'm in standby mode now. Call me when you need help.",
                "Going to standby mode. If you need help later, just call me.",
                "Going to standby. Contact me anytime you need assistance.",
                "Standby mode activated. Let me know if you need anything.",
                "Okay, I'm on standby now. Have a great day ahead!",
                "Entering standby mode now. Reach out to me when needed."
            ],
            "error": [
                "An error occurred. {error} Please try again.",
                "Oops! Something went wrong. {error} Please try again.",
                "An issue occurred. {error} Can you try again?",
                "Sorry, there was an error. {error} Please try again later.",
                "I ran into an error. {error} Can you try once more?",
                "Something went wrong. {error} Please try again.",
                "I'm afraid an error occurred. {error} Could you try again?",
                "Oops! An error happened. {error} Try again, please.",
                "Sorry, there was an issue. {error} Please try again.",
                "An error happened. {error} Please try again in a moment."
            ]
        }

        return random.choice(variations[category])

    def error_handling(self, error):
        """Handles errors gracefully."""
        error_message = self.get_random_variation("error").format(error=error)
        self.tts.speak(error_message)
        print(f"Error: {error_message}")

    def preprocess(self, text):
        """Preprocess user input."""

        text = text.lower().strip()
        text = re.sub(r'(?<!\w)\.|(?<=\s)\.|(?<!\w)\.(?!\w)', '', text)  # Removes unnecessary dots
        text = re.sub(r'[^\w\s.-_]', '', text)  # Removes punctuation except dot, hyphen
        text_arr = text.split()
        clean_arr = []
        for i in text_arr:
            if i not in clean_arr:
                clean_arr.append(i)
        text = ' '.join(clean_arr)

        return text

    def create_ui_and_process(self):
        """Handles the main assistant logic."""
        greeting = self.get_random_variation("greeting")
        self.tts.speak(greeting)
        print(f"Assistant: {greeting}")

        while self.is_running:
            try:
                if self.is_response:
                    self.user_query = self.user_query + " "+ self.stt.create_ui()
                else:
                    self.user_query = self.stt.create_ui()

                if not self.user_query:
                    self.tts.speak(self.get_random_variation("understanding"))
                    continue

                print(f'User query: {self.user_query}')
                self.user_query = self.preprocess(self.user_query)
                self.output_text = self.model.predict_bash_command(self.user_query)
                print(self.output_text)
                if self.output_text.startswith('response'):
                    response_text = self.output_text.replace("response:", "").strip()
                    if response_text.startswith('what'):
                        self.tts.speak(response_text)
                        self.is_response = True
                        continue
                    else:
                        self.tts.speak(response_text)
                        continue
                self.is_response = False
                self.output_text = self.output_text.replace("bash:", "").strip()
                print(f'Output query: {self.output_text}')
                self.text_to_speak = self.action.predict_action(self.output_text)

                if not self.text_to_speak:
                    raise ValueError("No action predicted for the output.")

                self.tts.speak(self.text_to_speak)
                self.tts.speak(self.get_random_variation("standby"))

                # Go into standby mode
                self.is_running = False
                print("DARLA is now in standby mode. Say 'Hey Darla' to wake me up.")

            except Exception as e:
                self.error_handling(str(e))
                continue

    def listen_for_wake_word(self):
        """Continuously listens for wake words to restart or stop the assistant."""
        print("Listening for wake words...")
        self.recorder.start()

        try:
            while not self.exit_flag:  # Keep running until exit_flag is set
                pcm = self.recorder.read()
                keyword_index = self.porcupine.process(pcm)

                if keyword_index == 0 and not self.is_running:  # "Hey Darla" in standby mode
                    print("Wake word detected: Restarting assistant...")
                    self.is_running = True
                    self.queue.put("start_ui")

                elif keyword_index == 1:  # "Stop Darla" at any time
                    print("Exit wake word detected: Shutting down assistant...")
                    self.exit_flag = True  # Set exit flag
                    self.cleanup()
                    break  # Exit the loop

        except KeyboardInterrupt:
            print("Wake word detection stopped.")
            self.exit_flag = True

        finally:
            if self.exit_flag:  # Only cleanup if we're actually exiting
                self.cleanup()

    def cleanup(self):
        """Cleans up resources before exiting."""
        print("Cleaning up resources...")
        if self.recorder.is_recording:
            self.recorder.stop()
        self.recorder.delete()
        self.porcupine.delete()
        self.action.cleanup_tmux_session()
        self.stt.on_close()
        self.tts.speak(self.get_random_variation("exit"))
        print("Assistant has stopped.")

    def run(self):
        print("DARLA is starting...")
    
        # Start the assistant normally
        self.create_ui_and_process()

        # Keep checking the queue for wake word detection
        while not self.exit_flag:
            try:
                task = self.queue.get_nowait()
                if task == "start_ui":
                    self.create_ui_and_process()  # Now runs in the main thread
            except queue.Empty:
                pass  # No tasks yet
            
            time.sleep(0.1)  # Prevent high CPU usage

        print("DARLA has exited.")


if __name__ == "__main__":
    assistant = Darla(audio=True)
    try:
        assistant.run()  # Assistant starts when the user clicks the icon
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        assistant.exit_flag = True
    finally:
        # Ensure a clean exit
        if not assistant.exit_flag:
            assistant.exit_flag = True