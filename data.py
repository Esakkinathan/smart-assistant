from datasets import load_dataset

# Load the dataset
ds = load_dataset("AnishJoshi/nl2bash-custom")

# Convert the dataset to a pandas DataFrame
df = ds["train"].to_pandas()  # Use 'train', 'test', or 'validation' as needed

# Save the DataFrame to CSV
df.to_csv("nl2bash_custom_dataset.csv", index=False)
