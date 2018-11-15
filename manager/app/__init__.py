
from flask import Flask
from flask_apscheduler import APScheduler

webapp = Flask(__name__)
#webapp.config['UPLOAD_FOLDER'] = '/home/john/Desktop/ECE_1779_A2/Web_application_ImageBay/webapp/app/static/upload_images'
webapp.secret_key = '\x80\xa9s*\x12\xc7x\xa9d\x1f(\x03\xbeHJ:\x9f\xf0!\xb1a\xaa\x0f\xee'


from app import EC2_Process
from app import sql_del