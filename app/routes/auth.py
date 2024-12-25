from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from flask_login import login_user, logout_user
from app.models import User, Pilot, Admin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db
bp = Blueprint('auth', __name__, template_folder='../templates')


@bp.route('/', methods=['GET', 'POST'])
def role_select():
    if request.method == 'POST':
        role = request.form['role']
        if role == 'user':
            return redirect(url_for('auth.Login_user'))
        elif role == 'pilot':
            return redirect(url_for('auth.Login_pilot'))
        elif role == 'admin':
            return redirect(url_for('auth.Login_admin'))
    return render_template('role_select.html')


@bp.route('/Login_user', methods=['GET', 'POST'])
def Login_user():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('auth.register'))
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                session['user_type'] = 'user'
                return redirect(url_for('user.dashboard'))
            else:
                flash('Invalid password')
                return render_template('login.html')
        else:
            flash('Username does not exist')
            return render_template('login.html')
    if request.method == 'GET':
        return render_template('login.html')


@bp.route('/Login_pilot', methods=['GET', 'POST'])
def Login_pilot():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('auth.register'))
        username = request.form['username']
        password = request.form['password']
        pilot = Pilot.query.filter_by(login_credentials=username).first()
        if pilot and check_password_hash(pilot.password, password):
            login_user(pilot)
            session['user_type'] = 'pilot'
            return redirect(url_for('pilot.dashboard'))
        else:
            flash('Invalid username or password')
    if request.method == 'GET':
        return render_template('login_admin_pilot.html')


@bp.route('/Login_admin', methods=['GET', 'POST'])
def Login_admin():
    if request.method == 'POST':
        if 'register' in request.form:
            return redirect(url_for('auth.register'))
        username = request.form['username']
        password = request.form['password']
        admin = Admin.query.filter_by(login_credentials=username).first()
        if admin and password == admin.password:
            login_user(admin)
            session['user_type'] = 'admin'
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password')
            return render_template('login_admin_pilot.html')
    if request.method == 'GET':
        return render_template('login_admin_pilot.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if 'login' in request.form:
            return redirect(url_for('auth.login_user'))
        username = request.form['username']
        contact_info = request.form['contact_info']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists')
            return render_template('login.html')
        else:
            # 对密码进行加密
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, password=hashed_password, contact_info=contact_info)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.login_user'))
    if request.method == 'GET':
        return render_template('register.html')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.role_select'))
