import random
from audio_processing import TextToSpeech
from audio_processing import SpeechToText
from model_processing import ModelProcessor
from action_processing import ActionProcessor
import threading
import time
class Darla:
    def __init__(self):
        self.stt = SpeechToText()
        self.tts = TextToSpeech(lang="en", tld='co.in', slow=False)
        self.action = ActionProcessor()
        self.model = ModelProcessor()
        self.is_running = True
        self.user_query = ''
        self.output_text = ''
        self.text_to_speak = ""

        # Variations for different phrases
        self.variations = {
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
            "continue": [
                "Do you want to continue, or is there anything else I can help with?",
                "Would you like to continue or do you need anything else?",
                "Is there anything else you'd like help with or should we continue?",
                "Shall we continue or is there anything else I can assist you with?",
                "Would you like to continue or is there anything else on your mind?",
                "Should I continue or is there something else you'd like to ask?",
                "Anything else I can do, or should I continue?",
                "Do you need any more help or shall I continue?",
                "Shall we keep going or is there something else you need?",
                "Would you like to keep going or do you need further assistance?"
            ],
            "standby": [
                "Okay, going to standby mode. Call me if you need anything. Have a great day!",
                "Entering standby mode now. If you need anything, just call me. Have a good day!",
                "I’m going to standby mode now. Reach out if you need anything. Have a wonderful day!",
                "Okay, I’m in standby mode now. Call me when you need help. Have a great day!",
                "Going to standby mode. If you need help later, just call me. Have a good day!",
                "I’m now in standby mode. Have a wonderful day!",
                "Going to standby. Contact me anytime you need assistance. Have a good day!",
                "Standby mode activated. Let me know if you need anything. Have a great day!",
                "Okay, I’m on standby now. Have a great day ahead!",
                "Entering standby mode now. Reach out to me when needed. Have a good day!"
            ],
            "error": [
                "An error occurred. {error} Please try again.",
                "Oops! Something went wrong. {error} Please try again.",
                "An issue occurred. {error} Can you try again?",
                "Sorry, there was an error. {error} Please try again later.",
                "I ran into an error. {error} Can you try once more?",
                "Something went wrong. {error} Please try again.",
                "I’m afraid an error occurred. {error} Could you try again?",
                "Oops! An error happened. {error} Try again, please.",
                "Sorry, there was an issue. {error} Please try again.",
                "An error happened. {error} Please try again in a moment."
            ]
        }

    def get_random_variation(self, category):
        """Selects a random variation from the provided category."""
        return random.choice(self.variations[category])

    def error_handling(self, error):
        """Handles errors gracefully by speaking an error message and logging it."""
        error_message = self.get_random_variation("error")
        error_message.format(error)
        self.tts.speak(f"{error_message}")
        print(f"Error: {error_message}")

    def create_ui_and_process(self):
        time.sleep(1)
        while self.is_running:
            try:
                greeting = self.get_random_variation("greeting")
                self.tts.speak(text=greeting)
                print(f"Assistant: {greeting}")
                time.sleep(3)
                self.user_query = self.stt.create_ui()
                if not self.user_query:
                    self.tts.speak(self.get_random_variation("understanding"))
                    continue
                print(f'user query: {self.user_query}')
                
                self.output_text = self.model.predict_bash_command(self.user_query)
                if not self.output_text:
                    raise ValueError("No valid bash command predicted.")
                print(f'output query: {self.output_text}')
                
                self.text_to_speak = self.action.predict_action(self.output_text)
                if not self.text_to_speak:
                    raise ValueError("No action predicted for the output.")
                
                self.tts.speak(self.text_to_speak)
                
                continue_prompt = self.get_random_variation("continue")
                self.tts.speak(continue_prompt)
                temp = self.stt.create_ui()
                if temp and temp.lower() == 'no':
                    standby_message = self.get_random_variation("standby")
                    self.tts.speak(standby_message)
                    self.is_running = False
            
            except Exception as e:
                self.error_handling(str(e))
                continue

    def run(self):
        thread = threading.Thread(target=self.create_ui_and_process, daemon=True)
        thread.start()
        thread.join()
        self.action.cleanup_pipe()

if __name__ == "__main__":
    assistant = Darla()
    print("DARLA is starting...")
    assistant.tts.speak("DARLA is ready.")
    assistant.run()
    print("DARLA has stopped.")
