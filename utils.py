import os
import platform
import re
import pdfkit
from werkzeug.security import generate_password_hash, check_password_hash


if platform.system() == 'Windows':
    DEFAULT_WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    DEFAULT_WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', DEFAULT_WKHTMLTOPDF_PATH)

try:
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except IOError:
    raise SystemExit(f'''
    ❌ wkhtmltopdf not found at: {WKHTMLTOPDF_PATH}
    Please install wkhtmltopdf and configure the path:
    1. Download from https://wkhtmltopdf.org/downloads.html
    2. Install with default settings
    3. Set environment variable:
       For Windows:
         WKHTMLTOPDF_PATH='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
       For Linux/Mac:
         WKHTMLTOPDF_PATH='/usr/local/bin/wkhtmltopdf'
    ''')
def validate_mobile(number):
    pattern = r'^[+]?[(]?\d{3}[)]?[-\s.]?\d{3}[-\s.]?\d{4,6}$'
    return re.match(pattern, number)

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
