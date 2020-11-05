import smtplib
import ssl
from string import Template
from utils.appConfig import DefaultConfig
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio
from utils.log_helper import *

import sendgrid
import os
from sendgrid.helpers.mail import *


logger = prepareLogger(__name__, 'mailing.log', logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'))

def sendGridLoginEmail(content,email_to):
    username = DefaultConfig.GMAIL_ID
    msg_template = read_template(DefaultConfig.LOGIN_TEMPLATE_FILENAME)
    messageContent = msg_template.substitute(IP_ADDRESS=content)
    message = Mail(
    from_email=username,
    to_emails=email_to,
    subject=DefaultConfig.LOGIN_EMAIL_TITLE,
    html_content=messageContent)
    # print(messageContent)
    try:
        sg = sendgrid.SendGridAPIClient(DefaultConfig.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code == 202)
        # print("This is email response:")
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        # print("This is email response end:")
        return True if response.status_code == 202 else False
    except Exception as e:
        logger.error("Error sending email in {}".format(__name__))
        return False


# def sendLoginEmail(content, email_to):
#     msg = MIMEMultipart()
#     port = DefaultConfig.SMTP_PORTS
#     server_name = DefaultConfig.SMTP_SERVER
#     # context = ssl.SSLContext(ssl.PROTOCOL_TLS)
#     username = DefaultConfig.GMAIL_ID
#     password = DefaultConfig.GMAIL_PW
#     return True
#     try:
#         with smtplib.SMTP(server_name,port[2]) as server:
#             # server.connect(server_name,port[2])
#             server.ehlo()
#             server.starttls()
#             server.ehlo
#             server.login(username, password)
#             msg_template = read_template(DefaultConfig.LOGIN_TEMPLATE_FILENAME)
#             message = msg_template.substitute(IP_ADDRESS=content)

#             msg['From'] = username
#             msg['To'] = email_to
#             msg['Subject'] = DefaultConfig.LOGIN_EMAIL_TITLE

#             msg.attach(MIMEText(message, 'plain'))
#             server.send_message(msg)
#             server.sendmail(username,email_to,msg)
#             del msg
#     except smtplib.SMTPException as e:
#         logger.error(e)
#         print(e)
#         return False
#     return True

def sendGridResetPw(content,email_to):
    username = DefaultConfig.GMAIL_ID
    msg_template = read_template(DefaultConfig.RESET_TEMPLATE_FILENAME)
    messageContent = msg_template.substitute(reset_link=content)
    message = Mail(
    from_email=username,
    to_emails=email_to,
    subject=DefaultConfig.LOGIN_EMAIL_TITLE,
    html_content=messageContent)
    # print(messageContent)
    try:
        sg = sendgrid.SendGridAPIClient(DefaultConfig.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code == 202)
        # print("This is email response:")
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        # print("This is email response end:")
        return True if response.status_code == 202 else False
    except Exception as e:
        logger.error("Error sending email in {}".format(__name__))
        return False

def send_reset_pw_email(content,email_to):
    msg = MIMEMultipart()
    port = DefaultConfig.SMTP_PORTS
    server_name = DefaultConfig.SMTP_SERVER
    username = DefaultConfig.GMAIL_ID
    password = DefaultConfig.GMAIL_PW
    # password = "_Pass1234"
    return True
    try:
        with smtplib.SMTP(host=server_name, port=port[2]) as server:
            # server.connect(server_name,port[2])
            server.ehlo()
            server.starttls()
            server.ehlo
            server.login(username, password)
            msg_template = read_template(DefaultConfig.RESET_TEMPLATE_FILENAME)
            message = msg_template.substitute(reset_link=content)

            msg['From']=username
            msg['To']=email_to
            msg['Subject']=DefaultConfig.RESET_EMAIL_TITLE

            msg.attach(MIMEText(message,'plain'))
            server.send_message(msg)
            server.sendmail(username,email_to,msg)
            del msg
    except Exception as e:
        logger.error(e)
        print(e)
        return False

    return True



def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

# def sendGridTest2():
#     sg = sendgrid.SendGridAPIClient(api_key=DefaultConfig.SENDGRID_API_KEY)
#     from_email = Email("clone_zone@hotmail.com")
#     to_email = To("clone_zone@hotmail.com")
#     subject = "Sending with SendGrid is Fun"
#     content = Content("text/plain", "and easy to do anywhere, even with Python")
#     mail = Mail(from_email, to_email, subject, content)
#     response = sg.client.mail.send.post(request_body=mail.get())
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
#     return True

def sendGridTest(content,email_to):
    username = DefaultConfig.GMAIL_ID
    password = DefaultConfig.GMAIL_PW
    message = Mail(
    from_email=username,
    to_emails=email_to,
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>'+str(content))
    try:
        sg = sendgrid.SendGridAPIClient(DefaultConfig.SENDGRID_API_KEY)
        response = sg.send(message)
        # print(response.status_code == 202)
        # print("This is email response:")
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)
        # print("This is email response end:")
        return True if response.status_code == 202 else False
    except Exception as e:
        logger.error("Error sending email in {}".format(__name__))
        return False
