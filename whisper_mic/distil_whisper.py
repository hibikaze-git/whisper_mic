import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


class DistilWhisper:
    def __init__(self) -> None:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_id = "distil-whisper/distil-large-v2"

        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            model_id, torch_dtype=torch_dtype, use_safetensors=True, cache_dir="./cache"
        )
        model.to(device)

        processor = AutoProcessor.from_pretrained(model_id, cache_dir="./cache")

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            max_new_tokens=128,
            torch_dtype=torch_dtype,
            device=device,
        )

    def __preprocess(self, data):
        return np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0

    def transcribe(self, audio_data):
        audio_data = self.__preprocess(audio_data)
        result = self.pipe(audio_data)
        return result
