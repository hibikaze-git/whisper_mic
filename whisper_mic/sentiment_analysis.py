import torch
from transformers import AutoModelForSequenceClassification, BertJapaneseTokenizer, pipeline, AutoTokenizer


class SentimentAnalyzer:
    def __init__(self) -> None:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "koheiduck/bert-japanese-finetuned-sentiment"

        model = AutoModelForSequenceClassification.from_pretrained(
            model_id, torch_dtype=torch_dtype, cache_dir="./cache"
        )
        model.to(device)

        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir="./cache")

        self.pipe = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            torch_dtype=torch_dtype,
            device=device,
        )

    def extract(self, text):
        try:
            result = self.pipe(text)
        except Exception as e:
            print(e)
            # dummyの結果
            result = [{'label': 'NEUTRAL', 'score': 0.9087327122688293}]
        return result
