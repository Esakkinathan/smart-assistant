""" from transformers import T5Tokenizer, T5ForConditionalGeneration

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
 """

import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

# Check and use GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Load the trained model and tokenizer
model_dir = "./model/darla-model"
tokenizer = T5Tokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir).to(device)

# Function to make predictions
def predict_bash_command(nl_command):
    # Preprocess the input command
    input_ids = tokenizer.encode(nl_command, return_tensors="pt", max_length=128, truncation=True).to(device)

    # Generate prediction
    output_ids = model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)

    # Decode the predicted Bash command
    bash_command = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return bash_command

# Load testing dataset
testing_file = "./data/test-data.csv"  # Replace with your testing dataset file
output_file = "./data/predicted-test-data.py"  # File to save the results
data = pd.read_csv(testing_file)

# Ensure the dataset has the correct structure
if not {'nl_cmd', 'bash_cmd'}.issubset(data.columns):
    raise ValueError("Dataset must contain 'nl_cmd' and 'bash_cmd' columns.")

# Predict and add the results
predicted_bash_commands = []
for nl_command in data['nl_cmd']:
    predicted_bash = predict_bash_command(nl_command)
    predicted_bash_commands.append(predicted_bash)

# Add the predictions as a new column
data['predicted_bash_cmd'] = predicted_bash_commands

# Save the updated dataset
data.to_csv(output_file, index=False)
print(f"Predicted results saved to {output_file}")

# Evaluate the model
correct_predictions = data[data['bash_cmd'] == data['predicted_bash_cmd']]
accuracy = len(correct_predictions) / len(data) * 100
print(f"Model Accuracy: {accuracy:.2f}%")

# Confusion Matrix and Error Analysis
y_true = data['bash_cmd']
y_pred = data['predicted_bash_cmd']

# Generate a confusion matrix
cm = confusion_matrix(y_true, y_pred, labels=y_true.unique())

# Plot confusion matrix
plt.figure(figsize=(12, 8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=y_true.unique(), yticklabels=y_true.unique())
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.show()

# Classification Report
report = classification_report(y_true, y_pred, zero_division=0)
print("\nClassification Report:\n")
print(report)
