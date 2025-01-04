from transformers import T5Tokenizer, T5ForConditionalGeneration

class ModelProcessor:
    def __init__(self):
        model_dir = "./model/t5-small-new-software-installer"
        self.tokenizer = T5Tokenizer.from_pretrained(model_dir)
        self.model = T5ForConditionalGeneration.from_pretrained(model_dir)

    def predict_bash_command(self, input_text):
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt", max_length=128, truncation=True).to(self.device)        
        output_ids = self.model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
        bash_command = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return bash_command
