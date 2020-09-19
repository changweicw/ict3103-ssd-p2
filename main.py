from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager
from flask_mysqldb import MySQL
# from flask_wtf import CSRFProtect

import re

from appConfig import DefaultConfig
from db_helper import *
from wtform import *

app = Flask(__name__, template_folder="templates")

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
# login = LoginManager(app)
# tesitng
mysql = MySQL(app)

src = "http://127.0.0.1:8080/"


@app.route('/')
def landing():
    session['title'] = "Collaboratory Mall"
    return render_template('landing.html')


@ app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account/my-account.html')


@ app.route('/login', methods=['GET', 'POST'])
def login_landing():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if login_form.validate_on_submit():
        login_result = check_login(login_form.username.data,
                                   login_form.password.data, mysql.connection.cursor())
        if login_result:
            # Handle Redirect after login success
            print('TODO LOGIN')
        else:
            flash('Your username or password is incorrect.', 'login')

    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src)


@ app.route("/register", methods=['GET', 'POST'])
def registration():
    login_form = LoginForm()
    registration_form = RegistrationForm()
    if registration_form.validate_on_submit():
        emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        emailPat = re.compile(emailRegex)
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        email_matched = re.search(emailPat, registration_form.email.data)
        password_matched = re.search(
            passwordPat, registration_form.password.data)
        if not email_matched:
            flash('Please enter a valid email', 'register')
        if registration_form.password.data != registration_form.confirmPassword.data:
            flash('Please enter the same password for both fields', 'register')
        else:
            if not password_matched:
                flash(
                    'Password must contain minimum 8 characters, with 1 uppercase, 1 lowercase, 1 digit & 1 special char', 'register')
            elif email_matched:
                # cont registration
                flash('Registered', 'register')
    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src)


@ app.route("/sell/publish_listing", methods=['POST'])
def publish():
    # files = request.form.getlist("files")
    files = request.files.getlist("files")
    print(files)
    return render_template('landing.html')


@ app.route('/sell/dashboard')
def sell_dashboard():
    return render_template('sell/sell_dashboard.html')


@ app.route('/products/checkout')
def checkout():
    return render_template('products/checkout.html')


if __name__ == '__main__':
    app.secret_key = b'_5#y2L"4Q8z178s/\\n\xec]/'
    app.run(host='127.0.0.1', port=8080, debug=True)
