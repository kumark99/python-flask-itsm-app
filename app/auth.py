from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlsplit
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                current_app.logger.warning(f"Failed login attempt for username: {form.username.data}")
                flash('Invalid username or password', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            current_app.logger.info(f"User logged in: {user.username}")
            next_page = request.args.get('next')
            if not next_page or urlsplit(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        return render_template('login.html', title='Sign In', form=form)
    except Exception as e:
        current_app.logger.error(f"Error during login: {str(e)}")
        flash('An error occurred during login.', 'danger')
        return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    try:
        username = current_user.username if current_user.is_authenticated else 'Unknown'
        logout_user()
        current_app.logger.info(f"User logged out: {username}")
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f"Error during logout: {str(e)}")
        return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data, role=form.role.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            current_app.logger.info(f"New user registered: {user.username}")
            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('auth.login'))
        return render_template('register.html', title='Register', form=form)
    except Exception as e:
        current_app.logger.error(f"Error during registration: {str(e)}")
        db.session.rollback()
        flash('An error occurred during registration.', 'danger')
        return render_template('register.html', title='Register', form=form)
