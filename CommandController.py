#!/usr/bin/env python3
import sys
import subprocess
from model_processing import ModelProcessor
from action_processing import ActionProcessor
from AudioController import Darla
class DarlaCommand(Darla):
    def __init__(self):
        super().__init__(audio = False)
        self.model_output = ""
        self.running = True
        self.action_response = ""
    def error_handling(self, error):
        error_message = self.get_random_variation("error").format(error=error)
        print(f"Error: {error_message}")


    def execute_action(self,command):
        while self.running: 
            try:
                command = self.preprocess(command)
                print("input command is: ",command)
                self.model_output = self.model.predict_bash_command(command)
                print('model output is: ',self.model_output)
                if self.model_output.startswith('response'):                            
                    response_text = self.model_output.replace("response:", "").strip()
                    if response_text.startswith('what'):
                            print(response_text)
                            self.command = self.command + " " + input(f'{response_text}? :')
                            continue
                    else:
                        print(response_text)
                        self.running = False
                        continue
                self.model_output = self.model_output.replace("bash:", "").strip()
                #print(f'Output query: {self.output_text}')
                self.action_response = self.action.predict_action(self.model_output)
                if not self.action_response:
                        print("No action predicted for the output.")
                        self.is_running = False
                        continue
                else:
                    print(self.action_response)
                print(self.get_random_variation("standby"))
                self.running = False
            except Exception as e:
                self.error_handling(str(e))
                continue



if __name__ == "__main__":
    darla = DarlaCommand()
    if len(sys.argv) > 1:
        user_command = " ".join(sys.argv[1:])
        darla.execute_action(user_command)
    else:
        print("Please provide a command.")

