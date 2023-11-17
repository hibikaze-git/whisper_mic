import numpy as np
import torch
from faster_whisper import WhisperModel


class FasterWhisper:
    def __init__(self) -> None:
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        model_size = "large-v2"

        self.model = WhisperModel(model_size, device="cuda", compute_type="float16", download_root="./cache")

    def __preprocess(self, data):
        return np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0

    def transcribe(self, audio_data):
        audio_data = self.__preprocess(audio_data)
        segments, info = self.model.transcribe(audio_data, beam_size=5, language="ja")

        for segment in segments:
            print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))
