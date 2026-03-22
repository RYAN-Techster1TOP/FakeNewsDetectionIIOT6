import sys
import os
import pandas as pd
import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

from utils.preprocess import clean_text

# ---------------- PATH SETUP ----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------- LOAD KAGGLE DATA ----------------
fake = pd.read_csv(os.path.join(BASE_DIR, "dataset", "Fake.csv"))
true = pd.read_csv(os.path.join(BASE_DIR, "dataset", "True.csv"))

fake = fake[["text"]]
true = true[["text"]]

fake["label"] = 0
true["label"] = 1

df_kaggle = pd.concat([fake, true])


# ---------------- LOAD LIAR DATA ----------------
liar = pd.read_csv(
    os.path.join(BASE_DIR, "dataset", "liar", "train.tsv"),
    sep="\t",
    header=None
)

liar = liar[[2, 1]]  # text, label
liar.columns = ["text", "label"]

# Convert multi-class → binary
liar["label"] = liar["label"].apply(
    lambda x: 1 if x in ["true", "mostly-true"] else 0
)

# ---------------- LOAD FAKENEWSNET ----------------
def load_fn(file_path, label):
    df = pd.read_csv(file_path)
    
    # detect column name safely
    if "text" in df.columns:
        text_col = "text"
    elif "title" in df.columns:
        text_col = "title"
    else:
        return pd.DataFrame(columns=["text", "label"])
    
    df = df[[text_col]]
    df.columns = ["text"]
    df["label"] = label
    
    return df


fn_fake1 = load_fn(os.path.join(BASE_DIR, "dataset", "fakenewsnet", "gossipcop_fake.csv"), 0)
fn_real1 = load_fn(os.path.join(BASE_DIR, "dataset", "fakenewsnet", "gossipcop_real.csv"), 1)

fn_fake2 = load_fn(os.path.join(BASE_DIR, "dataset", "fakenewsnet", "politifact_fake.csv"), 0)
fn_real2 = load_fn(os.path.join(BASE_DIR, "dataset", "fakenewsnet", "politifact_real.csv"), 1)

df_fn = pd.concat([fn_fake1, fn_real1, fn_fake2, fn_real2])


# ---------------- MERGE ALL DATA ----------------
final_df = pd.concat([df_kaggle, liar, df_fn])

# Clean text
final_df["text"] = final_df["text"].apply(clean_text)

# Remove empty
final_df = final_df[final_df["text"].str.strip() != ""]

# Shuffle
final_df = final_df.sample(frac=1).reset_index(drop=True)

print("Total samples:", len(final_df))


# ---------------- TRAIN MODEL ----------------
X = final_df["text"]
y = final_df["label"]

vectorizer = TfidfVectorizer(max_features=10000)
X_vec = vectorizer.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_vec, y, test_size=0.2, random_state=42
)

model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

accuracy = model.score(X_test, y_test)
print("Model Accuracy:", accuracy)


# ---------------- SAVE MODEL ----------------
joblib.dump(model, os.path.join(BASE_DIR, "models", "fake_news_model.pkl"))
joblib.dump(vectorizer, os.path.join(BASE_DIR, "models", "tfidf_vectorizer.pkl"))

print("Model Saved Successfully ✅")