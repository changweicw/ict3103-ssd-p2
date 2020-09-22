import smtplib
import ssl
from string import Template
from appConfig import DefaultConfig

port = [25,465,587]
server = "smtp.gmail.com"
context = ssl.create_default_context()
username = DefaultConfig.GMAIL_ID
password = DefaultConfig.GMAIL_PW

def sendEmail():
    return None
