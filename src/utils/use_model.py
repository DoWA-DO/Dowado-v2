from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

class Model:
    def __init__(self):        
        ''' 파인튜닝해서 Hugging Face에 업로드한 모델 로드 '''
        model_name = "ormor/dowado-v1-kiwi"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
    def classify_text(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding='max_length', truncation=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        logits = outputs.logits
        predicted_class_id = torch.argmax(logits, dim=-1).item()
        return predicted_class_id

    def classify_dataframe(self, text):
        predictions = []
        predicted_class_id = self.classify_text(text)
        predictions.append(predicted_class_id)
        return predictions
