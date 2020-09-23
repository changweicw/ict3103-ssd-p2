import sys
import os
from dotenv import load_dotenv

load_dotenv()


class DefaultConfig:
    """Default Configuration"""
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DB = os.getenv('MYSQL_DB')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
    MYSQL_CURSORCLASS = os.getenv('MYSQL_CURSORCLASS')
    SECRET_KEY = os.getenv('SECRET_KEY')
    GOOGLE_BUCKET_ID = os.getenv('GOOGLE_BUCKET_ID')
    GOOGLE_BUCKET_URL = os.getenv('GOOGLE_BUCKET_URL')
    GOOGLE_BUCKET_JSON_PATH = os.getenv('GOOGLE_BUCKET_JSON')
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="bucket_key.json"
    ALLOWED_EXTENSIONS = os.getenv('ALLOWED_EXTENSIONS').split(",")
    TEMP_UPLOAD_FOLDER_NAME = os.getenv('TEMP_UPLOAD_FOLDER_NAME')
    GMAIL_ID = os.getenv('GMAIL_ID')
    GMAIL_PW = os.getenv('GMAIL_PW')
    LOGIN_TEMPLATE_FILENAME = os.getenv('LOGIN_TEMPLATE_FILENAME')
    LOGIN_EMAIL_TITLE = os.getenv('LOGIN_EMAIL_TITLE')
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORTS = os.getenv('SMTP_PORTS').split(',')
    LOGGING_FOLDER = os.getenv('LOGGING_FOLDER')
    SESSION_TIMEOUT = os.getenv('SESSION_TIMEOUT')
    TESTING=os.getenv('TESTING')
    LOGING_DISABLED=os.getenv('LOGIN_DISABLED')
