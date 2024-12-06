import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration, Trainer, TrainingArguments
from datasets import Dataset
import torch

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load your dataset
train_data_path = r'dataset/taining-data.csv'
val_data_path = r'dataset/validation-data.csv'

train_df = pd.read_csv(train_data_path)
val_df = pd.read_csv(val_data_path)

# Convert pandas DataFrame to Hugging Face Dataset
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# Load T5 tokenizer and model
model_name = 't5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Move model to GPU
model = model.to(device)

# Tokenize the dataset
def tokenize_function(example):
    source = example['nl_cmd']
    target = example['bash_cmd']
    model_inputs = tokenizer(source, max_length=128, truncation=True, padding='max_length')
    labels = tokenizer(target, max_length=128, truncation=True, padding='max_length')

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_train = train_dataset.map(tokenize_function, batched=True)
tokenized_val = val_dataset.map(tokenize_function, batched=True)

# Define the training arguments
training_args = TrainingArguments(
    output_dir='./results',
    eval_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=20,
    weight_decay=0.01,
    logging_dir='./logs',
    save_total_limit=3,
    # Enable GPU if available
    fp16=torch.cuda.is_available(),
)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
)

# Train the model
trainer.train()

# Save the model
trainer.save_model("./model/t5-small-new-software-installer")
tokenizer.save_pretrained("./model/t5-small-new-software-installer")
