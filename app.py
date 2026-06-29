from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "simple_secret_key"

users = {
    "admin": {"password": "admin123", "role": "admin"},
    "rizal": {"password": "123456", "role": "user"}
}

DEMO_OTP = "123456"
activity_logs = []


def log_activity(user, action):
    activity_logs.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "action": action
    })


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username in users and users[username]["password"] == password:
            session["pending_user"] = username
            session["pending_role"] = users[username]["role"]
            log_activity(username, "Login successful")
            return redirect(url_for("otp"))

        log_activity(username, "Invalid login attempt")
        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


@app.route("/otp", methods=["GET", "POST"])
def otp():
    if "pending_user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        otp_code = request.form["otp"]

        if otp_code == DEMO_OTP:
            session["username"] = session["pending_user"]
            session["role"] = session["pending_role"]

            log_activity(session["username"], "OTP verified")

            session.pop("pending_user", None)
            session.pop("pending_role", None)

            return redirect(url_for("dashboard"))

        log_activity(session["pending_user"], "Invalid OTP attempt")
        return render_template("otp.html", error="Invalid OTP")

    return render_template("otp.html")


@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    if session["role"] == "admin":
        return render_template("admin.html", username=session["username"])

    return render_template("user.html", username=session["username"])


@app.route("/activity")
def activity():
    if "username" not in session:
        return redirect(url_for("login"))

    if session["role"] != "admin":
        return redirect(url_for("dashboard"))

    return render_template("activity.html", logs=activity_logs)


@app.route("/logout")
def logout():
    if "username" in session:
        log_activity(session["username"], "Logout")

    session.clear()
    return redirect(url_for("login"))


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)