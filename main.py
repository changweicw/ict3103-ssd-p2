from flask_login import LoginManager

from flask import Flask, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect

import re

from appConfig import *

import wtform_validator as forms

app = Flask(__name__, template_folder="templates")
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
# login = LoginManager(app)
mysql = MySQL(app)

src = "http://127.0.0.1:8080/"


@app.route('/')
def landing():
    title = "EhPlusMall"
    return render_template('shared/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = forms.LoginForm()
    # if login_form.validate_on_submit():
    #     # res = log_con.verify_login(
    #     #     mysql, login_form.username.data, login_form.password.data)
    #     # print(res)
    #     flash(login_form.password.data)

    return render_template('logins/account_page.html', form=login_form, src=src)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = forms.RegistrationForm()
    if registration_form.validate_on_submit():
        emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        emailPat = re.compile(emailRegex)
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        # return redirect(url_for('landing'))
    return render_template('registration.html', form=registration_form, src=src)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
