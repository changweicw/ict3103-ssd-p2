from flask import Flask, render_template, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect

from appConfig import DefaultConfig

import wtform_validator as forms

app = Flask(__name__,template_folder="templates")

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
mysql = MySQL(app)




@app.route('/', methods=['GET', 'POST'])
def landing():
    title = "EhPlusMall"
    # return redirect("/shop/")
    return render_template('landing.html')

@app.route('/account',methods=['GET','POST'])
def account():
    return render_template('account/my-account.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # login_form = forms.LoginForm()
    # if login_form.validate_on_submit():
    #     # res = log_con.verify_login(
    #     #     mysql, login_form.username.data, login_form.password.data)
    #     # print(res)
    #     flash(login_form.password.data)

    return render_template('account/login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = forms.RegistrationForm()
    if registration_form.validate_on_submit():
        flash(registration_form.password.data)
        # return redirect(url_for('login'))
    return render_template('registration.html', form=registration_form)

@app.route('/sell/dashboard')
def sell_dashboard():
    return render_template('sell/sell_dashboard.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
