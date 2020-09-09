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
    MYSQL_PORT = os.getenv('MYSQL_PORT')
    MYSQL_CURSORCLASS = os.getenv('MYSQL_CURSORCLASS')
    SECRET_KEY = os.getenv('SECRET_KEY')
