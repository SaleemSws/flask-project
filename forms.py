from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    DateTimeField,
    TextAreaField,
    SubmitField,
    SelectField,
)
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=20)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Register")


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Description")
    due_date = DateTimeField(
        "Due Date", format="%Y-%m-%dT%H:%M", validators=[DataRequired()]
    )
    priority = SelectField(
        "Priority",
        choices=[(str(i), "⭐" * i) for i in range(6)],
        validators=[DataRequired()],
    )
    submit = SubmitField("Submit")
