from flask import Blueprint, abort, current_app, render_template, request, flash, redirect, session, url_for
from firebase_utils import get_firestore_db,firestore
from utils import validate_mobile,check_password_hash, generate_password_hash,hash_password, check_password

auth_bp = Blueprint('auth', __name__)
db = get_firestore_db()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form['login_id'].strip()
        password = request.form['password'].strip()
        
        try:
            if '@' in login_id:
                user_ref = db.collection('users').where('email', '==', login_id).limit(1)
            else:
                if not validate_mobile(login_id):
                    flash('Invalid mobile number format', 'danger')
                    return redirect(url_for('auth.login'))
                user_ref = db.collection('users').where('mobile', '==', login_id).limit(1)
            
            users = user_ref.get()
            
            if not users:
                flash('Account not found', 'danger')
                return redirect(url_for('auth.login'))
            
            user = users[0].to_dict()
            if check_password_hash(user['password'], password):
                session['user'] = {
                    'uid': users[0].id,
                    'email': user['email'],
                    'name': user['full_name'],
                    'is_admin': user.get('is_admin', False)
                }
                
                if session['user']['is_admin']:
                    return redirect(url_for('admin.admin_dashboard'))
                
                next_url = request.args.get('next')
                return redirect(next_url or url_for('main.home'))
            else:
                flash('Invalid password', 'danger')
                
        except Exception as e:
            flash('Login failed', 'danger')
            current_app.logger.error(f'Login error: {str(e)}')
    
    return render_template('login.html', next=request.args.get('next'))



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form['full_name'].strip()
        email = request.form['email'].strip().lower()
        mobile = request.form['mobile'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        errors = False
        if not full_name or len(full_name) < 3:
            flash('Full name must be at least 3 characters', 'danger')
            errors = True
            
        if not validate_mobile(mobile):
            flash('Invalid mobile number format', 'danger')
            errors = True
            
        if len(password) < 8:
            flash('Password must be at least 8 characters', 'danger')
            errors = True
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            errors = True
            
        email_ref = db.collection('users').where('email', '==', email).limit(1)
        mobile_ref = db.collection('users').where('mobile', '==', mobile).limit(1)
        
        if email_ref.get():
            flash('Email already registered', 'danger')
            errors = True
            
        if mobile_ref.get():
            flash('Mobile number already registered', 'danger')
            errors = True
        
        if 'terms' not in request.form:
            flash('You must accept the terms and privacy policy', 'danger')
            errors = True
            
        if errors:
            return redirect(url_for('auth.register'))
        
        try:
            user_data = {
                'full_name': full_name,
                'email': email,
                'mobile': mobile,
                'password': generate_password_hash(password),
                'is_admin': False,
                'plan_limit': 1,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
            db.collection('users').add(user_data)
            flash('Registration successful! Please login', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            current_app.logger.error(f'Registration error: {str(e)}')
    
    return render_template('register.html')
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def check_admin_status(uid):
    try:
        user_ref = db.collection('users').document(uid)
        user_doc = user_ref.get()
        if user_doc.exists:
            return user_doc.to_dict().get('is_admin', False)
        return False
    except Exception as e:
        current_app.logger.error(f"Admin check error: {str(e)}")
        return False


@auth_bp.route('/profile', methods=['GET', 'POST'])
def user_profile():
    if not session.get('user'):
        abort(401)
    
    try:
        user_ref = db.collection('users').document(session['user']['uid'])
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        user_data['plan_limit'] = user_data.get('plan_limit', 5)
        plans_ref = db.collection('plans').where('user_id', '==', session['user']['uid']).stream()
        plans = []
        for plan in plans_ref:
            plan_data = plan.to_dict()
            plan_data['id'] = plan.id
            plans.append(plan_data)
        
        if request.method == 'POST':
            current_password = request.form['current_password']
            if not check_password_hash(user_data['password'], current_password):
                flash('Current password is incorrect', 'danger')
                return redirect(url_for('auth.user_profile'))
            
            new_password = request.form['new_password']
            if new_password:
                if len(new_password) < 8:
                    flash('New password must be at least 8 characters', 'danger')
                    return redirect(url_for('auth.user_profile'))
                
                user_ref.update({
                    'password': generate_password_hash(new_password),
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
                flash('Password updated successfully', 'success')
            
            return redirect(url_for('auth.user_profile'))
        
        return render_template('profile.html', 
                             user=user_data, 
                             plans=plans)
        
    except Exception as e:
        current_app.logger.error(f"Profile error: {str(e)}")
        flash('Error accessing profile', 'danger')
        return redirect(url_for('main.home'))