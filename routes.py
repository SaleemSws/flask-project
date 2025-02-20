from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task, User
from forms import TaskForm
from datetime import datetime
from flask_login import login_required, logout_user, login_user, current_user

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def index():
    return render_template("index.html")


@app_routes.route("/dashboard", methods=["GET", "POST"])
@login_required
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

    tasks = Task.query.filter_by(completed=False)  # ดึงงานทั้งหมดจากฐานข้อมูล
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
        new_user.set_password(password)  # ใช้ set_password() เพื่อแฮชรหัสผ่านก่อนบันทึก
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("app_routes.login"))

    return render_template("register.html")


@app_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("app_routes.dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("app_routes.login"))


@app_routes.route("/add_task", methods=["POST"])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(title=form.title.data, completed=False, user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!", "success")
    return redirect(url_for("app_routes.dashboard"))


# สร้างเส้นทางสำหรับการเพิ่มงานใหม่
