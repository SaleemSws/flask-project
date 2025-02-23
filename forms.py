from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    DateTimeField,
    TextAreaField,
    SubmitField,
    SelectField,
)
from wtforms.validators import DataRequired, Length, ValidationError
from models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(
                min=3, max=20, message="Username must be between 3 and 20 characters"
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6, message="Password must be at least 6 characters"),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "Username already exists. Please choose a different one."
            )


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
