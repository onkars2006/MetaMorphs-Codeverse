from flask import Blueprint, current_app, render_template, redirect, session, url_for, flash, request, abort
from firebase_utils import get_firestore_db
from routes.auth import check_admin_status

admin_bp = Blueprint('admin', __name__)
db = get_firestore_db()

@admin_bp.route('/admin')
def admin_dashboard():
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    users = []
    try:
        users_ref = db.collection('users').where('is_admin', '==', False).stream()
        for user_doc in users_ref:
            user_data = user_doc.to_dict()
            user_data['id'] = user_doc.id
            
            plans_ref = db.collection('plans').where('user_id', '==', user_doc.id)
            user_data['plan_count'] = len(list(plans_ref.stream()))
            user_data['plan_limit'] = user_data.get('plan_limit', 5)
            users.append(user_data)
            
        users.sort(key=lambda x: x.get('created_at'), reverse=True)
        
    except Exception as e:
        current_app.logger.error(f"Admin dashboard error: {str(e)}")
        flash('Error loading user data', 'danger')
    
    return render_template('admin.html', users=users)

@admin_bp.route('/admin/users/<user_id>')
def admin_user_profile(user_id):
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    try:
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            flash('User not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
            
        user_data = user_doc.to_dict()
        user_data['id'] = user_id
        
        plans_ref = db.collection('plans').where('user_id', '==', user_id).stream()
        plans = []
        for plan in plans_ref:
            plan_data = plan.to_dict()
            plan_data['id'] = plan.id
            plans.append(plan_data)
        
        return render_template('user_profile.html', user=user_data, plans=plans)
        
    except Exception as e:
        current_app.logger.error(f"User profile error: {str(e)}")
        flash('Error loading user profile', 'danger')
        return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/users/<user_id>/delete', methods=['POST'])
def admin_delete_user(user_id):
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    try:
        db.collection('users').document(user_id).delete()
        
        plans_ref = db.collection('plans').where('user_id', '==', user_id).stream()
        for plan in plans_ref:
            plan.reference.delete()
        
        flash('User and associated data deleted successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"User deletion error: {str(e)}")
        flash('Error deleting user', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/plans/<plan_id>/delete', methods=['POST'])
def delete_plan(plan_id):
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    try:
        plan_ref = db.collection('plans').document(plan_id)
        plan_doc = plan_ref.get()
        
        if not plan_doc.exists:
            flash('Plan not found', 'danger')
            return redirect(url_for('admin.admin_dashboard'))
        
        plan_ref.delete()
        flash('Plan deleted successfully', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Plan delete error: {str(e)}")
        flash(f'Error deleting plan: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/plans/<plan_id>/edit')
def edit_plan(plan_id):
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    try:
        plan_ref = db.collection('plans').document(plan_id)
        plan = plan_ref.get().to_dict()
        return render_template('editor.html', 
                            plan_id=plan_id,
                            plan=plan,
                            admin_edit=True)
    except Exception as e:
        current_app.logger.error(f"Admin edit error: {str(e)}")
        flash('Error accessing plan', 'danger')
        return redirect(url_for('admin.admin_dashboard'))



@admin_bp.route('/admin/users/<user_id>/update_limit', methods=['POST'])
def update_plan_limit(user_id):
    if not session.get('user') or not check_admin_status(session['user']['uid']):
        abort(403)
    
    try:
        new_limit = int(request.form.get('plan_limit'))
        if new_limit < 0:
            raise ValueError
            
        db.collection('users').document(user_id).update({
            'plan_limit': new_limit
        })
        flash('Plan limit updated successfully', 'success')
    except (ValueError, TypeError):
        flash('Invalid plan limit value', 'danger')
    except Exception as e:
        current_app.logger.error(f"Plan limit update error: {str(e)}")
        flash('Error updating plan limit', 'danger')
    
    return redirect(url_for('admin.admin_dashboard'))