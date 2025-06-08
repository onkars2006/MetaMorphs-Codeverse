from flask import Flask
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.plans import plans_bp
from routes.main import main_bp
import os

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

import markdown as md

@app.template_filter('markdown')
def markdown_filter(text):
    return md.markdown(text)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(main_bp)

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)