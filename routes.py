from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task, User
from forms import TaskForm
from datetime import datetime

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def index():
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


@app_routes.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    task = Task.query.get(task_id)
    form = TaskForm(obj=task)

    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash("Task updated!", "info")
        return redirect(url_for("app_routes.dashboard"))

    return render_template("edit_task.html", form=form, task=task)


@app_routes.route("/history")
def history():
    completed_tasks = (
        Task.query.filter_by(completed=True).order_by(Task.completed_at.desc()).all()
    )
    return render_template("history.html", tasks=completed_tasks)


@app_routes.route("/search", methods=["GET", "POST"])
def search_tasks():
    query = request.args.get("query", "").strip()  # ดึงค่าจาก input
    tasks = []

    if query:  # ถ้ามีการค้นหา
        tasks = Task.query.filter(
            Task.title.ilike(f"%{query}%")
        ).all()  # ค้นหาแบบ case-insensitive

    return render_template("search.html", tasks=tasks, query=query)


@app_routes.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("app_routes.dashboard"))


@app_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("app_routes.register"))

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("app_routes.login"))

    return render_template("register.html")
