import re
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")

stop_words = set(stopwords.words("english"))

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub("[^a-zA-Z]", " ", text)
    return text

    # words = text.split()
    # words = [w for w in words if w not in stop_words]

    # return " ".join(words)