from datasets import load_dataset
import pandas as pd

# Load the NL2Bash dataset from Hugging Face
dataset = load_dataset("jiacheng-ye/nl2bash")

# Convert to Pandas DataFrame
df = pd.DataFrame(dataset["train"])

# Ensure the data is sorted by the existing 'sr_no' column

# Save as CSV file
df.to_csv("nl2bash_dataset.csv", index=False)

print("Dataset saved as nl2bash_dataset.csv")
