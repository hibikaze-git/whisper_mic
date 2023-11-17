import random

from pythonosc import udp_client


EMOTION_DICT = {
    "喜び": [6, 7, 8],
    "信頼": [],
    "恐れ": [10],
    "驚き": [],
    "悲しみ": [11, 12],
    "嫌悪": [13, 14],
    "怒り": [15],
    "期待": [],
    "苦悩": [16],
    "羞恥": [],
    "平常": [0, 1, 2, 3, 4]
}

SENTIMENT_DICT = {
    #"POSITIVE": ["喜び", "信頼", "期待"],
    "POSITIVE": ["喜び"],
    "NEGATIVE": ["恐れ", "悲しみ", "嫌悪", "怒り", "苦悩"],
    #"NEUTRAL": ["平常", "驚き", "羞恥"],
    "NEUTRAL": ["平常"],
}


class VRChatManager:
    def __init__(self) -> None:
        ip = "127.0.0.1"
        port = 9000
        self.client = udp_client.SimpleUDPClient(ip, port)

    def change_expression(self, emotions, sentiments):
        expression_num = 0

        if emotions:
            emotion_list = EMOTION_DICT.get(emotions[0]["aggregate"])

            if emotion_list is not None and emotion_list:
                expression_num = random.choice(emotion_list)

        elif sentiments:
            sentiment = sentiments[0]["label"]

            if sentiment in ["NEGATIVE", "POSITIVE"]:
                threshold = 0.65
            else:
                threshold = 0

            if sentiments[0]["score"] > threshold:
                sentiment_to_emotion = random.choice(SENTIMENT_DICT.get(sentiment))
                expression_num = random.choice(EMOTION_DICT.get(sentiment_to_emotion))

        self.client.send_message("/avatar/parameters/FaceEmo_SYNC_EM_EMOTE", expression_num)
