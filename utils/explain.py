import numpy as np

def explain_prediction(text, vectorizer, model):

    tfidf = vectorizer.transform([text])

    feature_names = vectorizer.get_feature_names_out()
    vec = vectorizer.transform([text])

    coefs = model.coef_[0]
    scores = tfidf.toarray()[0] * coefs
    indices = vec.indices[:10]

    words = [feature_names[i] for i in indices]

    return words