from flask import render_template, Blueprint, url_for, \
    redirect, flash, request
from flask_login import login_user, logout_user, \
    login_required, current_user
import datetime
from models.models import User
# from project.email import send_email
from .user_forms import LoginForm, RegisterForm, ChangePasswordForm
from .user_token import generate_confirmation_token, confirm_token
from .user_email import send_email
from .user_decorators import check_confirmed
from .oauth import OAuthSignIn

user_blueprint = Blueprint('user', __name__,)


@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    from server import db
    if request.method == "GET":
        return render_template('user/register.html')
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            social_id=form.email.data,
            email=form.email.data,
            nickname=form.username.data,
            password=form.password.data,
            confirmed=False
        )
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)
        return redirect(url_for("user.unconfirmed"))
    else:
        for error in form.email.errors:
            flash(error, 'error')
        for error in form.username.errors:
            flash(error, 'error')
        for error in form.password.errors:
            flash(error, 'error')
        for error in form.confirm.errors:
            flash(error, 'error')
        return render_template('user/register.html')


@user_blueprint.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('user.login'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@user_blueprint.route('/callback/<provider>')
def oauth_callback(provider):
    from server import db
    if not current_user.is_anonymous:
        return redirect(url_for('user.login'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.', 'error')
        return redirect(url_for('user.login'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, email=email, nickname=username,
                    password=social_id, admin=False, confirmed=True,
                    confirmed_on=datetime.datetime.now())
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('main.home'))


@user_blueprint.route('/confirm/<token>')
#@login_required
def confirm_email(token):
    from server import db
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('user.unconfirmed'))
    user = User.query.filter_by(social_id=email).first_or_404()
    if user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
        return redirect(url_for('user.login'))
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')
        return redirect(url_for('user.profile'))


@user_blueprint.route('/unconfirmed')
#@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('main.home'))
    flash('Please confirm your account!', 'error')
    return render_template('user/unconfirmed.html')


@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    from server import bcrypt
    if request.method == "GET":
        return render_template('user/login.html')
    form = LoginForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(social_id=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email and/or password.', 'error')
            return render_template('user/login.html')
    else:
        for error in form.email.errors:
            flash(error, 'error')
        for error in form.password.errors:
            flash(error, 'error')
        return render_template('user/login.html')


@user_blueprint.route('/logout')
#@login_required
def logout():
    logout_user()
    flash('You were logged out.', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
#@login_required
#@check_confirmed
def profile():
    from server import db, bcrypt
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(social_id=current_user.social_id).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password successfully changed.', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Password change was unsuccessful.', 'error')
            return redirect(url_for('user.profile'))
    else:
        for error in form.password.errors:
            flash(error, 'error')
        for error in form.confirm.errors:
            flash(error, 'error')
        return render_template('user/profile.html')


@user_blueprint.route('/resend')
#@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('user.unconfirmed'))
