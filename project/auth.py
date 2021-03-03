from flask import Blueprint, render_template, url_for, redirect, request, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()    # check if email exists in db
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login'))
    login_user(user, remember=remember)
    current_app.logger.info(f'user {user.name} logged in')
    return redirect(url_for('main.home'))


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first()    # check if email exists in db
    if user:
        flash('Email address already exists.')      # send message to next redirect
        return redirect(url_for('auth.signup'))

    new_user = User(
        email=email,
        password=generate_password_hash(password, method='sha256'),
        name=name
    )

    db.session.add(new_user)
    db.session.commit()

    current_app.logger.info(f'user {new_user.name} signed up')
    return redirect(url_for('auth.login'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    current_app.logger.info(f'user {current_user.name} signed up')
    return redirect(url_for('main.index'))
