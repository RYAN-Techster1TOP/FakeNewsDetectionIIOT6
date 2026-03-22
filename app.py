from flask import Flask, render_template, request, redirect, session
import joblib
import uuid
import re
from datetime import datetime
from database.db import users, history
from utils.preprocess import clean_text
from utils.explain import explain_prediction
from utils.news_api import check_real_news
from bson.objectid import ObjectId
app = Flask(__name__)
app.secret_key = "supersecret"
# Load model
model = joblib.load("models/fake_news_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")
# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        role = request.form.get("role")
        user = users.find_one({"email": email})
        if user and user["password"] == password:
            # Check if role matches
            if role != user["role"]:
                return render_template("login.html",
                    error="Incorrect role selected")
            session["user"] = email
            session["role"] = role
            # Admin goes to admin dashboard
            if user["role"] == "admin":
                return redirect("/admin")
            # User goes to prediction page
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")
# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = {
            "name": request.form["name"],
            "email": request.form["email"],
            "password": request.form["password"],
            "role": "user"
        }
        users.insert_one(user)
        return redirect("/login")
    return render_template("signup.html")
# ---------------- PREDICTION PAGE ----------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")
# ---------------- PREDICT NEWS ----------------
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/login")
    text = request.form["news"].strip()
    if text == "":
        return render_template("index.html", error="Please enter some news text.")
    cleaned = clean_text(text)
    vec = vectorizer.transform([cleaned])
    probs = model.predict_proba(vec)[0]
    fake_prob = probs[0]
    real_prob = probs[1]
    if real_prob > fake_prob:
        result = "Real News"
        confidence = round(real_prob*100, 2)
    else:
        result = "Fake News"
        confidence = round(fake_prob*100, 2)
    # Explainable AI
    important_words = explain_prediction(cleaned, vectorizer, model)
    # Real-time fact check
    keywords = " ".join(w for w in text.split() if len(w) > 4)[:6]
    articles = check_real_news(keywords)
    # Save history
    history.insert_one({
        "user": session["user"],
        "text": text,
        "result": result,
        "confidence": confidence,
        "time": datetime.now()
    })
    return render_template(
        "result.html",
        prediction=result,
        confidence=confidence,
        words=important_words,
        articles=articles
    )
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")
    page = request.args.get("page", default=1, type=int)
    per_page = 8
    query = {"user": session["user"]}
    total = history.count_documents(query)
    cursor = history.find(query)
    user_history = list(cursor.skip((page - 1) * per_page).limit(per_page))
    total_pages =  max(1, (total + per_page - 1) // per_page)
    return render_template("dashboard.html", history=user_history, page=page, total_pages=total_pages)
# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/login")
    if session.get("role") != "admin":
        return redirect("/")
    total_users = users.count_documents({})
    total_predictions = history.count_documents({})
    fake_count = history.count_documents({"result": "Fake News"})
    real_count = history.count_documents({"result": "Real News"})
    return render_template(
        "admin_dashboard.html",
        users=total_users,
        predictions=total_predictions,
        fake=fake_count,
        real=real_count
    )
@app.route("/admin/users")
def admin_users():
    if "user" not in session or session.get("role") != "admin":
        return redirect("/login")
    all_users = list(users.find())
    return render_template("admin_users.html", users=all_users)
@app.route("/delete-user/<id>")
def delete_user(id):
    if "user" not in session or session.get("role") != "admin":
        return redirect("/login")
    users.delete_one({"_id": ObjectId(id)})
    return redirect("/admin/users")
# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot-password", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        email = request.form["email"]
        user = users.find_one({"email": email})
        if user:
            token = str(uuid.uuid4())
            users.update_one(
                {"email": email},
                {"$set": {"reset_token": token}}
            )
            link = f"http://127.0.0.1:5000/reset-password/{token}"
            print("RESET LINK:", link)
            return "Reset link printed in terminal."
    return render_template("forgot_password.html")
# ---------------- RESET PASSWORD ----------------
@app.route("/reset-password/<token>", methods=["GET","POST"])
def reset(token):
    user = users.find_one({"reset_token": token})
    if not user:
        return "Invalid token"
    if request.method == "POST":
        new_pass = request.form["password"]
        users.update_one(
            {"reset_token": token},
            {"$set":{"password": new_pass, "reset_token":""}}
        )
        return redirect("/login")
    return render_template("reset_password.html")
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run()