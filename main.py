from flask import Flask, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect

from appConfig import *

import wtform_validator as forms

app = Flask(__name__)
# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = forms.LoginForm()
    if login_form.validate_on_submit():
        # res = log_con.verify_login(
        #     mysql, login_form.username.data, login_form.password.data)
        # print(res)
        flash(login_form.password.data)

    return render_template('login.html', form=login_form)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = forms.RegistrationForm()
    if registration_form.validate_on_submit():
        flash(registration_form.password.data)
        # return redirect(url_for('login'))
    return render_template('registration.html', form=registration_form)


@app.route('/landing')
def landing():
    return 'Hello Landing'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
