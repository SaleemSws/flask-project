from flask import Flask
from config import Config
from models import db, User
from routes import app_routes
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

# กำหนด static folder ให้ชัดเจน
app = Flask(__name__)

app.config.from_object(Config)

Bootstrap(app)
db.init_app(app)
app.register_blueprint(app_routes)
migrate = Migrate(app, db)  # เพิ่ม Migrate ให้กับ appss

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "app_routes.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
