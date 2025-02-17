from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task
from forms import TaskForm
from datetime import datetime

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def home():
    return render_template("index.html")


@app_routes.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!", "success")
        return redirect(url_for("app_routes.dashboard"))

    tasks = Task.query.all()  # ดึงงานทั้งหมดจากฐานข้อมูล
    return render_template("dashboard.html", form=form, tasks=tasks)


@app_routes.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted!", "danger")
    return redirect(url_for("app_routes.dashboard"))


@app_routes.route("/history")
def history():
    return render_template("history.html")


@app_routes.route("/search")
def search():
    return render_template("search.html")
