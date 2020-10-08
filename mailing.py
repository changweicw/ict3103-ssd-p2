import smtplib
import ssl
from string import Template
from appConfig import DefaultConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio


def sendLoginEmail(content, email_to):
    msg = MIMEMultipart()
    port = DefaultConfig.SMTP_PORTS
    server_name = DefaultConfig.SMTP_SERVER
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    username = DefaultConfig.GMAIL_ID
    password = DefaultConfig.GMAIL_PW
    with smtplib.SMTP(server_name, port[1]) as server:
        try:
            # server.connect(server_name,port[2])
            server.ehlo()
            server.starttls()
            server.login(username, password)
            msg_template = read_template(DefaultConfig.LOGIN_TEMPLATE_FILENAME)
            message = msg_template.substitute(IP_ADDRESS=content)

            msg['From'] = username
            msg['To'] = email_to
            msg['Subject'] = DefaultConfig.LOGIN_EMAIL_TITLE

            msg.attach(MIMEText(message, 'plain'))
            server.send_message(msg)
            # server.sendmail(username,email_to,msg)
            del msg
        except Exception as e:
            print(e)
            return False
    return True


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)
