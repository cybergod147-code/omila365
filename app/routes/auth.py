# app/routes/auth.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from app.extensions import db
from app.models import User, Tenant
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ------------------- DECORATORS -------------------
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

def operator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('operator', 'admin'):
            return jsonify({'error': 'Operator or admin access required'}), 403
        return f(*args, **kwargs)
    return decorated

# ------------------- ROUTES -------------------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('operator.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if not user.is_active:
                flash('Account is disabled.', 'danger')
                return render_template('login.html')
            login_user(user)
            # Update last_login if column exists
            try:
                user.last_login = datetime.utcnow()
                db.session.commit()
            except Exception:
                db.session.commit()
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('operator.dashboard'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('operator.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm_password')

        # Validation
        if not all([username, email, password, confirm]):
            flash('All fields are required.', 'danger')
            return render_template('register.html')

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')

        # Create a new tenant for this user
        tenant = Tenant(
            name=f"{username}'s Tenant",
            is_active=True,
            plan='Trial'
        )
        db.session.add(tenant)
        db.session.commit()

        user = User(
            username=username,
            email=email,
            role='operator',
            is_active=True,
            tenant_id=tenant.id
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid request'}), 400

    current = data.get('current_password')
    new = data.get('new_password')
    confirm = data.get('confirm_password')

    if not all([current, new, confirm]):
        return jsonify({'error': 'All fields required'}), 400

    if new != confirm:
        return jsonify({'error': 'New passwords do not match'}), 400

    if len(new) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    if not current_user.check_password(current):
        return jsonify({'error': 'Current password is incorrect'}), 400

    current_user.set_password(new)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Password changed'})