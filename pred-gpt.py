from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load the trained model and tokenizer
model_dir = "./model/t5-small-new-software-installer"
tokenizer = T5Tokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)

# Function to make predictions
def predict_bash_command(nl_command):
    # Preprocess the input command
    input_text =nl_command
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=128, truncation=True)

    # Generate prediction
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)

    # Decode the predicted Bash command
    bash_command = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return bash_command

# Prediction loop
while True:
    # Take input from user
    nl_command = input("Enter a natural language command (or 'exit' to stop): ")

    # Exit condition
    if nl_command.lower() == 'exit':
        print("Exiting...")
        break

    # Predict and display the bash command
    predicted_bash = predict_bash_command(nl_command)
    print(f"Predicted Bash Command: {predicted_bash}\n")
