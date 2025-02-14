from flask import Flask
from flask import render_template

app = Flask(__name__)  # สร้าง app


@app.route("/")
def index():
    return "<h1>First Test<h1>"


if __name__ == "__main__":
    app.run(debug=True)  # รันโปรแกรม
