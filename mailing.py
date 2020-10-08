import smtplib
import ssl
from string import Template
from appConfig import DefaultConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio
from log_helper import *


logger = prepareLogger(__name__, 'mailing.log', logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))


def sendLoginEmail(content, email_to):
    msg = MIMEMultipart()
    port = DefaultConfig.SMTP_PORTS
    server_name = DefaultConfig.SMTP_SERVER
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    username = DefaultConfig.GMAIL_ID
    password = DefaultConfig.GMAIL_PW

    try:
        with smtplib.SMTP(server_name, port[0]) as server:
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
        logger.error(e)
        return False
    return True


def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


<< << << < HEAD
== == == =


# def sendGridTest(content,email_to):
#     username = DefaultConfig.GMAIL_ID
#     password = DefaultConfig.GMAIL_PW
#     message = Mail(
#     from_email=username,
#     to_emails=email_to,
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>'+str(content))
#     try:
#         sg = SendGridAPIClient(DefaultConfig.SENDGRID_API_KEY)
#         response = sg.send(message)
#         print("This is email response:")
#         print(response.status_code)
#         print(response.body)
#         print(response.headers)
#         print("This is email response end:")
#     except Exception as e:
#         print(e)
>>>>>> > 16d2a578cc58f169a7aa75282833531e177c1dc5
