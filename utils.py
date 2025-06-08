import os
import platform
import re
import pdfkit
from werkzeug.security import generate_password_hash, check_password_hash


if platform.system() == 'Windows':
    DEFAULT_WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    DEFAULT_WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

# Check if binary exists, fallback to /usr/bin/wkhtmltopdf if needed
if not os.path.exists(DEFAULT_WKHTMLTOPDF_PATH) and platform.system() != 'Windows':
    DEFAULT_WKHTMLTOPDF_PATH = '/usr/bin/wkhtmltopdf'

WKHTMLTOPDF_PATH = os.getenv('WKHTMLTOPDF_PATH', DEFAULT_WKHTMLTOPDF_PATH)

try:
    pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
except IOError:
    raise SystemExit(f'''
    ❌ wkhtmltopdf not found at: {WKHTMLTOPDF_PATH}
    Please install wkhtmltopdf and configure the path.
    ''')
def validate_mobile(number):
    pattern = r'^[+]?[(]?\d{3}[)]?[-\s.]?\d{3}[-\s.]?\d{4,6}$'
    return re.match(pattern, number)

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
