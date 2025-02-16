from app import app, db
from models import Todo
from flask import render_template, request, redirect, url_for


@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)


@app.route("/create", methods=["GET", "POST"])
def create_todo():
    if request.method == "POST":
        todo = Todo(
            title=request.form["title"], description=request.form["description"]
        )
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("create.html")
