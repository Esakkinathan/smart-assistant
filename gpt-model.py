import pandas as pd
from transformers import T5ForConditionalGeneration, Trainer, TrainingArguments, EarlyStoppingCallback, RobertaTokenizer
from datasets import Dataset
import torch

# Check if GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("cuda" if torch.cuda.is_available() else "cpu")
# Load your dataset
train_data_path = r'./data/train-data.csv'
val_data_path = r'./data/validation-data.csv'

train_df = pd.read_csv(train_data_path)
val_df = pd.read_csv(val_data_path)

# Convert pandas DataFrame to Hugging Face Dataset
train_dataset = Dataset.from_pandas(train_df)
val_dataset = Dataset.from_pandas(val_df)

# Load T5 tokenizer and mkodel
model_name = 'Salesforce/codet5-small'  
tokenizer = RobertaTokenizer.from_pretrained(model_name, legacy=False)
model = T5ForConditionalGeneration.from_pretrained(model_name)

# Move model to GPU
model = model.to(device)

# Tokenize the dataset
def tokenize_function(example):
    source = ["provide bash command or response(if unrecognized return default): " + line for line in example['nl_cmd']]
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
    save_strategy="epoch",  # Save model at the end of each epoch
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=20,
    weight_decay=0.01,
    logging_dir='./logs',
    save_total_limit=3,
    # Enable GPU if available
    fp16=torch.cuda.is_available(),
    load_best_model_at_end=True,  # Load the best model after early stopping
    metric_for_best_model="eval_loss",  # Metric to monitor
    greater_is_better=False,  # Lower eval_loss is better

)

# Initialize the Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    tokenizer=tokenizer,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],  
)

# Train the model
trainer.train()

# Save the model
trainer.save_model("./model/darla-model")
tokenizer.save_pretrained("./model/darla-model")
