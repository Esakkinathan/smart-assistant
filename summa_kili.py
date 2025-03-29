from transformers import T5ForConditionalGeneration,RobertaTokenizer
import pandas as pd


# Load the trained model and tokenizer
model_dir = "./model/darla-model"
tokenizer = RobertaTokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)

# Function to make predictions
def predict_bash_command(nl_command):
    nl_command = "provide bash command or response(if unrecognized return default): " + nl_command
    # Preprocess the input command
    input_ids = tokenizer.encode(nl_command, return_tensors="pt", max_length=128, truncation=True)

    # Generate prediction
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)

    # Decode the predicted Bash command
    bash_command = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return bash_command

while True:
    a = input("Enter NL Command or e to exit: ")
    if a == 'e':
        break
    print(predict_bash_command(a))

