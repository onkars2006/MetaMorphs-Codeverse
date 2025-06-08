from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for, session, jsonify, abort, send_file
from firebase_utils import get_firestore_db
from routes.auth import check_admin_status
from services.ai_generator import generate_startup_plan, generate_market_research, generate_tech_stack, generate_revenue_models
from services.export_service import generate_pdf, generate_word_document, generate_full_markdown, generate_qr_code
import uuid
import PyPDF2
import os
import traceback
from io import BytesIO
import uuid
from firebase_admin import firestore

plans_bp = Blueprint('plans', __name__)
db = get_firestore_db()

@plans_bp.route('/generate', methods=['POST'])
def generate():
    if not session.get('user'):
        flash('Please login or register to create a business plan', 'warning')
        return redirect(url_for('auth.login', next=request.url)) 
    if not session.get('user'):
        abort(401)
    
    """Handle plan generation request"""
    try:
        
        user_id = session['user']['uid']
        
        user_ref = db.collection('users').document(user_id)
        user_data = user_ref.get().to_dict()
        plan_limit = user_data.get('plan_limit', 5)
        plans_ref = db.collection('plans').where('user_id', '==', user_id)
        current_count = len(list(plans_ref.stream()))
        
        if current_count >= plan_limit:
            flash(f'Plan limit reached ({plan_limit}). Please contact admin to upgrade the existing plans.', 'danger')
            return redirect(url_for('main.home'))
        
        input_method = request.form.get('input_method', 'text')
        idea_type = request.form.get('idea_type', 'custom')

        
        form_data = {
            'startup_name': request.form['startup_name'].strip(),
            'idea_type': idea_type,
            'business_model': request.form.get('business_model', 'SaaS'),
            'industry': request.form.get('industry', ''),
            'budget': request.form.get('budget', ''),
            'funding_status': request.form.get('funding_status', ''),
            'term_type': request.form.get('term_type', ''),
            'input_method': input_method,
            'user_id': user_id  
        }

        if input_method == 'pdf':
            pdf_file = request.files.get('pdf_file')
            if not pdf_file or pdf_file.filename == '':
                flash('Please upload a PDF file', 'danger')
                return redirect(url_for('main.home'))

            if not pdf_file.filename.lower().endswith('.pdf'):
                flash('Invalid file type. Please upload a PDF', 'danger')
                return redirect(url_for('main.home'))

            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                pdf_text = ""
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"

                if not pdf_text.strip():
                    flash('The PDF contains no extractable text', 'danger')
                    return redirect(url_for('main.home'))

                form_data['startup_idea'] = pdf_text.strip()

            except Exception as e:
                flash(f'Error processing PDF: {str(e)}', 'danger')
                return redirect(url_for('main.home'))

        else:
            
            form_data['startup_idea'] = request.form['startup_idea'].strip()

        
        if idea_type == 'predefined':
            focus_area = request.form.get('predefined_focus', '').strip()
            form_data['startup_idea'] = f"{form_data['industry']} AI solution focusing on {focus_area}"

        
        html_content, raw_markdown, error = generate_startup_plan(form_data)
        if error:
            flash(f'Error generating plan: {error}', 'danger')
            return redirect(url_for('main.home'))

        
        market_research_raw, _ = generate_market_research(form_data['startup_idea'])
        tech_stack_raw, _ = generate_tech_stack(form_data['startup_idea'])
        revenue_models_raw, _ = generate_revenue_models(form_data['startup_idea'])

        
        plan_id = str(uuid.uuid4())
        plan_data = {
            'user_id': user_id,
            'html_content': html_content,
            'raw_markdown': raw_markdown,
            'market_research': market_research_raw,
            'tech_stack': tech_stack_raw,
            'revenue_models': revenue_models_raw,
            'customizations': {},
            'logo': None,
            'theme': 'default',
            'form_data': form_data,
            'view_key': str(uuid.uuid4()),
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }

        db.collection('plans').document(plan_id).set(plan_data)

        return redirect(url_for('plans.plan_editor', plan_id=plan_id))

    except KeyError as e:
        flash(f'Missing required field: {e}', 'danger')
        return redirect(url_for('main.home'))
    except Exception as e:
        current_app.logger.error(f"Firestore save error: {str(e)}")
        flash('Error saving business plan', 'danger')
        return redirect(url_for('main.home'))
    pass

@plans_bp.route('/plan/<plan_id>', methods=['GET', 'POST'])
def plan_editor(plan_id):
    """Handle plan editor functionality"""
    if not session.get('user'):
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login', next=request.url))
    
    try:
        user = session['user']
        user_id = user['uid']
        is_admin = user.get('is_admin', False)

        plan_ref = db.collection('plans').document(plan_id)
        plan_doc = plan_ref.get()

        if not plan_doc.exists:
            flash('Plan not found or has been deleted', 'danger')
            return redirect(url_for('main.home'))

        plan = plan_doc.to_dict()

        if plan['user_id'] != user_id and not is_admin:
            flash('You do not have permission to access this plan', 'danger')
            return redirect(url_for('main.home'))

        if request.method == 'POST':
            if 'logo' in request.files:
                logo = request.files['logo']
                if logo and logo.filename != '':
                    if '.' in logo.filename and logo.filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}:
                        from werkzeug.utils import secure_filename
                        filename = f"{plan_id}_{secure_filename(logo.filename)}"
                        logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                        logo.save(logo_path)
                        plan_ref.update({'logo': filename})
                        flash('Logo uploaded successfully', 'success')
                        return redirect(url_for('plans.plan_editor', plan_id=plan_id))

            if 'theme' in request.form:
                new_theme = request.form['theme']
                plan_ref.update({'theme': new_theme})

            if 'content' in request.form:
                updated_content = request.form['content']
                plan_ref.update({
                    'raw_markdown': updated_content,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })

            return jsonify({'status': 'success'})

        view_mode = request.args.get('view_key') == plan.get('view_key')

        user_ref = db.collection('users').document(plan['user_id'])
        user_data_doc = user_ref.get()
        user_data = user_data_doc.to_dict() if user_data_doc.exists else {}

        return render_template('editor.html',
                               plan_id=plan_id,
                               plan=plan,
                               user_data=user_data,
                               view_mode=view_mode)

    except Exception as e:
        error_message = f"Plan editor error: {str(e)}\n{traceback.format_exc()}"
        current_app.logger.error(error_message)
        flash('An unexpected error occurred while accessing the plan', 'danger')
        return redirect(url_for('main.home'))

    pass

@plans_bp.route('/view/<plan_id>')
def view_plan(plan_id):
    """Secure view-only access"""
    try:
        plan_ref = db.collection('plans').document(plan_id)
        plan = plan_ref.get().to_dict()
        
        if not plan:
            abort(404)
            
        if request.args.get('view_key') != plan.get('view_key'):
            abort(403, description="Invalid or expired view key")
            
        user_ref = db.collection('users').document(plan['user_id'])
        user_data = user_ref.get().to_dict()

        return render_template('editor.html',
                             plan_id=plan_id,
                             plan=plan,
                             user_data=user_data,
                             view_mode=True)
    except Exception as e:
        current_app.logger.error(f"View plan error: {str(e)}")
        abort(500)
    pass

@plans_bp.route('/export/<plan_id>/<format>')
def export_plan(plan_id, format):
    """Handle plan exports with AI sections"""
    try:
        plan_ref = db.collection('plans').document(plan_id)
        plan = plan_ref.get().to_dict()
        
        if not plan:
            abort(404)

        if not session.get('user') or (plan['user_id'] != session['user']['uid'] and not check_admin_status(session['user']['uid'])):
            if request.args.get('view_key') != plan.get('view_key'):
                abort(403)

        if format == 'pdf':
            return generate_pdf(plan)
        elif format == 'docx':
            return generate_word_document(plan)
        elif format == 'md':
            return send_file(
                BytesIO(generate_full_markdown(plan).encode()),
                mimetype='text/markdown',
                download_name='business_plan.md',
                as_attachment=True
            )
        elif format == 'qr':
            return generate_qr_code(plan_id, plan)
        else:
            abort(400)
    except Exception as e:
        current_app.logger.error(f"Export failed: {str(e)}")
        abort(500)
    pass