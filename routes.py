from app import app, db
from models import Todo


@app.route("/")
def index():
    todos = Todo.query.all()
    return render_template("index.html", todos=todos)
