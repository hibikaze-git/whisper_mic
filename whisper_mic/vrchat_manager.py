import random

from pythonosc import udp_client


EMOTION_DICT = {
    "平常": [1, 2, 3, 4, 5, 6, 7, 8, 9],
    "喜び": [11, 12, 13, 14, 15, 16],
    "信頼": [17],
    "期待": [18],
    "恐れ": [20],
    "悲しみ": [21, 22],
    "嫌悪": [23, 24],
    "怒り": [25],
    "苦悩": [26],
    "羞恥": [27],
    "驚き": [28],
}

NO_BLINK_NUMS = [16]

SENTIMENT_DICT = {
    "POSITIVE": ["喜び", "信頼", "期待"],
    "NEGATIVE": ["恐れ", "悲しみ", "嫌悪", "怒り", "苦悩", "驚き", "羞恥"],
    "NEUTRAL": ["平常"],
}


class VRChatManager:
    def __init__(self) -> None:
        ip = "127.0.0.1"
        port = 9000
        self.client = udp_client.SimpleUDPClient(ip, port)

    def choice_expression_by_sentiment(self, sentiments, expression_num):
        if sentiments:
            sentiment = sentiments[0]["label"]
            is_NEUTRAL = False

            if sentiment in ["NEGATIVE", "POSITIVE"]:
                threshold = 0.7
            else:
                threshold = 0
                is_NEUTRAL = True

            if sentiments[0]["score"] > threshold:
                emotion = random.choice(SENTIMENT_DICT.get(sentiment))
                expression_num = random.choice(EMOTION_DICT.get(emotion))

        return expression_num, is_NEUTRAL

    def change_expression(self, emotions, sentiments):
        expression_num = 0
        emotion = None
        change_expression_by_emotion = False
        is_NEUTRAL = False

        if emotions:
            emotion = emotions[0]["aggregate"]
            emotions_sentiment = None

            # emotionのネガポジを判定
            for key, val in SENTIMENT_DICT.items():
                if emotion in val:
                    emotions_sentiment = key

            if sentiments:
                sentiment = sentiments[0]["label"]

                # 文章のネガポジとemotionのネガポジが一致した場合のみemotinoに基づいて表情変更
                if emotions_sentiment == sentiment or sentiment == "NEUTRAL":
                    emotion_list = EMOTION_DICT.get(emotion)

                    if emotion_list is not None and emotion_list:
                        expression_num = random.choice(emotion_list)
                        change_expression_by_emotion = True

                else:
                    expression_num, is_NEUTRAL = self.choice_expression_by_sentiment(sentiments, expression_num)

        else:
            # sentimentのみで判定
            expression_num, is_NEUTRAL = self.choice_expression_by_sentiment(sentiments, expression_num)

        # まばたき制御
        if emotion in ["驚き"] or expression_num in NO_BLINK_NUMS:
            self.client.send_message("/avatar/parameters/FaceEmo_CN_BLINK_ENABLE", False)
        else:
            self.client.send_message("/avatar/parameters/FaceEmo_CN_BLINK_ENABLE", True)

        # 送信
        self.client.send_message("/avatar/parameters/FaceEmo_SYNC_EM_EMOTE", expression_num)
        print("send: ", expression_num)

        # 判定された感情に応じて感情解析を停止するか分岐
        if change_expression_by_emotion:
            disable_emotion_analysis = True
        elif is_NEUTRAL:
            disable_emotion_analysis = False
        else:
            disable_emotion_analysis = True

        return disable_emotion_analysis
