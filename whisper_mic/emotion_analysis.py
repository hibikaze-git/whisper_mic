import csv
import json

import ginza
import spacy
import textdistance


class EmotionAnalyzer:
    def __init__(self) -> None:
        self.emotion_annotation_dict = {}
        self.emotion_category_dict = {}

        with open("./var/emotion_annotation.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for annotation in reader:
                self.emotion_annotation_dict[annotation[0]] = annotation[2]

        with open("./var/emotion_category.csv", "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            for category in reader:
                self.emotion_category_dict[category[1]] = {"detail": category[0], "aggregate": category[2]}

        self.nlp = spacy.load("ja_ginza")
        ginza.set_split_mode(self.nlp, "C")

        self.filter_tags = ["助詞", "補助記号", "助動詞"]

    def _wakati_with_tag(self, text) -> str:
        """
        分かち書きした各トークンとともに品詞等を出力

        Args:
            text (str): 解析するテキスト

        Returns:
            dic: 文章番号と分かち書きしたトークン、品詞等の情報ををまとめた辞書型
        """
        doc = self.nlp(text)

        wakati_with_tag_list = {}

        for i, sent in enumerate(doc.sents):
            sent_wakati_with_tag_list = {}

            for token in sent:
                token_list = {}

                token_list["text"] = token.text
                token_list["lemma_"] = token.lemma_
                token_list["pos"] = token.pos
                token_list["tag_"] = token.tag_
                token_list["norm_"] = token.norm_

                sent_wakati_with_tag_list[token.i] = token_list

            wakati_with_tag_list[f"文章{i+1}"] = sent_wakati_with_tag_list

        return wakati_with_tag_list

    def extract_emotion(self, text):
        """
        analyzerの解析結果を基に、感情を特定
        """

        # analyzerで解析
        result = self._wakati_with_tag(text)
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # テキスト自身も含める
        word_list = [text]

        for key, value in result.items():
            for item in value.values():
                if item["tag_"].split("-")[0] not in self.filter_tags:
                    word_list.append(item["norm_"])

        print(word_list)

        emotion_list = []
        match_word = {"word": None, "emotion_word": None, "similarity": None}
        rate_dict = {}

        for emotion_word, emotion_tags in self.emotion_annotation_dict.items():
            for word in word_list:
                if len(word) > 3:
                    rate = round(textdistance.cosine.normalized_similarity(word, emotion_word), 8)
                    rate_dict["->".join([word, emotion_word, emotion_tags])] = rate

                if word == emotion_word:
                    emotion_tag_list = list(emotion_tags)
                    match_word["word"] = word
                    match_word["emotion_word"] = emotion_word
                    match_word["similarity"] = 1

                    for emotion_tag in emotion_tag_list:
                        emotion_list.append(self.emotion_category_dict.get(emotion_tag))

                    break

        if not emotion_list and rate_dict.items():
            max_key, rate = max(rate_dict.items(), key=lambda x: x[1])
            print(max_key, rate)

            [word, emotion_word, emotion_tags] = max_key.split("->")

            if rate > 0.8:
                emotion_tag_list = list(emotion_tags)
                match_word["word"] = word
                match_word["emotion_word"] = emotion_word
                match_word["similarity"] = rate

                for emotion_tag in emotion_tag_list:
                    emotion_list.append(self.emotion_category_dict.get(emotion_tag))

        print(match_word)

        return emotion_list
