import os
import platform
import re
import pdfkit
from werkzeug.security import generate_password_hash, check_password_hash


if platform.system() == 'Windows':
    WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
else:
    WKHTMLTOPDF_PATH = '/usr/local/bin/wkhtmltopdf'

# fallback if default Linux path doesn't exist but /usr/bin/wkhtmltopdf exists
if platform.system() != 'Windows' and not os.path.exists(WKHTMLTOPDF_PATH):
    WKHTMLTOPDF_PATH = '/usr/bin/wkhtmltopdf'

pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
def validate_mobile(number):
    pattern = r'^[+]?[(]?\d{3}[)]?[-\s.]?\d{3}[-\s.]?\d{4,6}$'
    return re.match(pattern, number)

def hash_password(password):
    return generate_password_hash(password)

def check_password(hashed_password, password):
    return check_password_hash(hashed_password, password)
