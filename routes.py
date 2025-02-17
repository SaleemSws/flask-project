from flask import Blueprint, render_template

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def home():
    return render_template("index.html")


@app_routes.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app_routes.route("/history")
def history():
    return render_template("history.html")


@app_routes.route("/search")
def search():
    return render_template("search.html")
