import torch
from transformers import T5ForConditionalGeneration,RobertaTokenizer
import pandas as pd

# Check and use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load the trained model and tokenizer
model_dir = "./model/darla-model"
tokenizer = RobertaTokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir).to(device)

# Function to make predictions
def predict_bash_command(nl_command):
    nl_command = "translate english to bash: " + nl_command
    # Preprocess the input command
    input_ids = tokenizer.encode(nl_command, return_tensors="pt", max_length=128, truncation=True).to(device)

    # Generate prediction
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)

    # Decode the predicted Bash command
    bash_command = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return bash_command

# Load testing dataset
testing_file = "./data/test-data.csv"  # Replace with your testing dataset file
output_file = "./data/predicted-test-data.csv"  # File to save the results
data = pd.read_csv(testing_file)


# Predict and add the results
predicted_bash_commands = []
i=1
for nl_command in data['nl_cmd']:
    predicted_bash = predict_bash_command(nl_command)
    predicted_bash_commands.append(predicted_bash)
    print(i)
    i+=1

# Add the predictions as a new column
data['predicted_bash_cmd'] = predicted_bash_commands

# Add the Match column to check if predictions are correct
data['Match'] = data['bash_cmd'].str.rstrip() == data['predicted_bash_cmd'].str.rstrip()

# Save the updated dataset
data.to_csv(output_file, index=False)
print(f"Predicted results saved to {output_file}")

print("Calculating accuracy...")

# Evaluate the model
accuracy = data['Match'].mean() * 100
print(f"Model Accuracy: {accuracy:.2f}%")


