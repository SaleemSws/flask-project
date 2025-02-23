from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Task, User
from forms import TaskForm, LoginForm, RegisterForm
from datetime import datetime
from flask_login import login_required, logout_user, login_user, current_user

app_routes = Blueprint("app_routes", __name__)


@app_routes.route("/")
def index():
    return render_template("index.html")


@app_routes.route("/dashboard")
@login_required
def dashboard():
    # แก้ไขการเรียงลำดับให้เรียงตาม priority มากไปน้อย และ due_date
    tasks = (
        Task.query.filter_by(user_id=current_user.id, completed=False)
        .order_by(
            Task.priority.desc(),  # เรียงจากความสำคัญมากไปน้อย
            Task.due_date.asc(),  # แล้วค่อยเรียงตามวันที่ใกล้สุดก่อน
        )
        .all()
    )

    # ดึงข้อมูล completed tasks
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id, completed=True
    ).count()

    # นับจำนวน urgent tasks (priority >= 3)
    urgent_tasks = Task.query.filter(
        Task.user_id == current_user.id, Task.completed == False, Task.priority >= 3
    ).count()

    return render_template(
        "dashboard.html",
        tasks=tasks,
        completed_tasks=completed_tasks,
        urgent_tasks=urgent_tasks,
    )


@app_routes.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=int(form.priority.data),  # เพิ่มการบันทึก priority
            created_at=datetime.utcnow(),
            user_id=current_user.id,
        )
        db.session.add(new_task)
        db.session.commit()
        flash("Task added successfully!", "success")
        return redirect(url_for("app_routes.dashboard"))
    return render_template("add_task.html", form=form)


@app_routes.route("/delete_task/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task and task.user_id == current_user.id:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted!", "danger")
    return redirect(url_for("app_routes.dashboard"))


@app_routes.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Access denied!", "danger")
        return redirect(url_for("app_routes.dashboard"))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = int(form.priority.data)  # เพิ่มการบันทึก priority
        db.session.commit()
        flash("Task updated!", "info")
        return redirect(url_for("app_routes.dashboard"))

    return render_template("edit_task.html", form=form, task=task)


@app_routes.route("/history")
@login_required
def history():
    completed_tasks = (
        Task.query.filter_by(user_id=current_user.id, completed=True)
        .order_by(Task.completed_at.desc())
        .all()
    )
    return render_template("history.html", tasks=completed_tasks)


@app_routes.route("/search", methods=["GET", "POST"])
def search_tasks():
    query = request.args.get("query", "").strip()
    tasks = []

    if query:
        tasks = Task.query.filter(Task.title.ilike(f"%{query}%")).all()

    return render_template("search.html", tasks=tasks, query=query)


@app_routes.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("Access denied!", "danger")
        return redirect(url_for("app_routes.dashboard"))

    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for("app_routes.dashboard"))


@app_routes.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username already exists!", "danger")
            return redirect(url_for("app_routes.register"))

        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("app_routes.login"))

    return render_template("register.html", form=form)


@app_routes.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("app_routes.dashboard"))
        flash("Invalid username or password", "danger")
    return render_template("login.html", form=form)


@app_routes.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("app_routes.login"))


@app_routes.route("/analytics")
@login_required
def analytics():
    # Statistics for tasks
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    completed_tasks = Task.query.filter_by(
        user_id=current_user.id, completed=True
    ).count()
    pending_tasks = Task.query.filter_by(
        user_id=current_user.id, completed=False
    ).count()

    # Priority distribution
    priority_dist = {
        i: Task.query.filter_by(user_id=current_user.id, priority=i).count()
        for i in range(1, 6)
    }

    # Monthly completion rate
    current_month = datetime.utcnow().month
    monthly_completed = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == True,
        db.extract("month", Task.completed_at) == current_month,
    ).count()

    return render_template(
        "analytics.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        priority_dist=priority_dist,
        monthly_completed=monthly_completed,
    )


@app_routes.route("/system-status")
@login_required
def system_status():
    # System metrics
    user_count = User.query.count()
    total_tasks_system = Task.query.count()
    active_tasks = Task.query.filter_by(completed=False).count()

    # User performance ranking (top 5)
    top_users = (
        db.session.query(User, db.func.count(Task.id).label("task_count"))
        .join(Task)
        .group_by(User)
        .order_by(db.text("task_count DESC"))
        .limit(5)
        .all()
    )

    return render_template(
        "system_status.html",
        user_count=user_count,
        total_tasks_system=total_tasks_system,
        active_tasks=active_tasks,
        top_users=top_users,
    )


@app_routes.route("/neural-assistant")
@login_required
def neural_assistant():
    # Get user's task patterns
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()

    # Calculate optimal task scheduling
    urgent_tasks = Task.query.filter(
        Task.user_id == current_user.id, Task.completed == False, Task.priority >= 4
    ).all()

    # Get upcoming deadlines
    upcoming_deadlines = (
        Task.query.filter(
            Task.user_id == current_user.id,
            Task.completed == False,
            Task.due_date > datetime.utcnow(),
        )
        .order_by(Task.due_date.asc())
        .limit(5)
        .all()
    )

    return render_template(
        "neural_assistant.html",
        urgent_tasks=urgent_tasks,
        upcoming_deadlines=upcoming_deadlines,
        task_count=len(user_tasks),
    )


@app_routes.route("/task-matrix")
@login_required
def task_matrix():
    # Get tasks based on urgency and importance
    urgent_important = Task.query.filter(
        Task.user_id == current_user.id, Task.priority >= 4, Task.completed == False
    ).all()

    urgent_not_important = Task.query.filter(
        Task.user_id == current_user.id,
        Task.priority <= 3,
        Task.due_date <= datetime.utcnow(),
        Task.completed == False,
    ).all()

    not_urgent_important = Task.query.filter(
        Task.user_id == current_user.id,
        Task.priority >= 4,
        Task.due_date > datetime.utcnow(),
        Task.completed == False,
    ).all()

    not_urgent_not_important = Task.query.filter(
        Task.user_id == current_user.id,
        Task.priority <= 3,
        Task.due_date > datetime.utcnow(),
        Task.completed == False,
    ).all()

    return render_template(
        "task_matrix.html",
        urgent_important=urgent_important,
        urgent_not_important=urgent_not_important,
        not_urgent_important=not_urgent_important,
        not_urgent_not_important=not_urgent_not_important,
    )
