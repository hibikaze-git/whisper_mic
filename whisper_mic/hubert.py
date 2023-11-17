import numpy as np
import torch
import librosa

from transformers import Wav2Vec2FeatureExtractor, HubertForSequenceClassification, Wav2Vec2ForSequenceClassification


class Hubert:
    def __init__(self) -> None:
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"

        model_name = 'Bagus/wav2vec2-xlsr-japanese-speech-emotion-recognition'
        #model_name = 'Rajaram1996/Hubert_emotion'
        #model_name = 'ehcalabres/wav2vec2-lg-xlsr-en-speech-emotion-recognition'

        feature_extractor_name = model_name
        #feature_extractor_name = "facebook/hubert-base-ls960"

        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(feature_extractor_name, cache_dir="./cache")
        self.model = HubertForSequenceClassification.from_pretrained(model_name, cache_dir="./cache").to(self.device)
        #self.model = Wav2Vec2ForSequenceClassification.from_pretrained(model_name, cache_dir="./cache").to(self.device)
        self.feature_extractor
        self.model.eval()

    def __preprocess(self, data):
        return np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0

    def transcribe(self, audio_data):
        audio_data = self.__preprocess(audio_data)
        #print(audio_data.shape[0])
        #audio_data = librosa.resample(audio_data, audio_data.shape[0], 16_000)
        #print(audio_data.shape[0])
        inputs = self.feature_extractor(audio_data, return_tensors="pt", sampling_rate=16000, padding=True).to(self.device)
        with torch.no_grad():
            logits = self.model(**inputs).logits
        predicted_class_ids = torch.argmax(logits, dim=-1)
        predicted_label = self.model.config.id2label[predicted_class_ids.item()]
        print(predicted_label)
