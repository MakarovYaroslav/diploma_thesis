from flask_wtf import Form
from wtforms import PasswordField, StringField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from models.models import User


class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(message="Email field is required"), Email(message='Email is not correct!')])
    password = PasswordField('password', validators=[DataRequired(message="Password field is required")])


class RegisterForm(Form):
    email = StringField(
        'email',
        validators=[DataRequired(message="Email field is required"),
                    Email(message='Email is not correct!'), Length(min=6, max=40, message="Email field must be between 6 and 40 characters long.")])
    username = StringField(
        'username',
        validators=[DataRequired(message="Username field is required"), Length(min=6, max=40, message="Username field must be between 6 and 40 characters long.")])
    password = PasswordField(
        'password',
        validators=[DataRequired(message="Password field is required"), Length(min=6, max=25, message="Password field must be between 6 and 25 characters long.")]
    )
    confirm = PasswordField(
        'confirm',
        validators=[
            DataRequired(message="Password confirmation field is required"),
            EqualTo('password', message='Passwords must match!')
        ]
    )

    def validate(self):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(social_id=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered!")
            return False
        return True


class ChangePasswordForm(Form):
    password = PasswordField(
        'password',
        validators=[DataRequired(message="Password field is required"), Length(min=6, max=25, message="Password field must be between 6 and 25 characters long.")]
    )
    confirm = PasswordField(
        'confirm',
        validators=[
            DataRequired(message="Confirm field is required"),
            EqualTo('password', message='Passwords must match.')
        ]
    )
