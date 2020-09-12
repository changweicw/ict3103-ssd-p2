from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect,FlaskForm
from wtforms import StringField,FileField,DecimalField

from appConfig import DefaultConfig

import wtform_validator as forms

app = Flask(__name__,template_folder="templates")

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
mysql = MySQL(app)

class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")


@app.route('/', methods=['GET', 'POST'])
def landing():
    session['title'] = "Collaboratory Mall"
    return render_template('landing.html')

@app.route('/account',methods=['GET','POST'])
def account():
    return render_template('account/my-account.html')

@app.route('/login', methods=['GET', 'POST'])
def login_landing():
    # login_form = forms.LoginForm()
    # if login_form.validate_on_submit():
    #     # res = log_con.verify_login(
    #     #     mysql, login_form.username.data, login_form.password.data)
    #     # print(res)
    #     flash(login_form.password.data)

    return render_template('account/login.html')

# This to be completed. 
@app.route("/sell/publish_listing", methods=['POST'])
def publish():
    # files = request.form.getlist("files")
    files = request.files.getlist("files")
    print(files)
    return render_template('landing.html')

@app.route('/sell/dashboard')
def sell_dashboard():
    return render_template('sell/sell_dashboard.html')

@app.route('/products/checkout')
def checkout():
    return render_template('products/checkout.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    registration_form = forms.RegistrationForm()
    if registration_form.validate_on_submit():
        flash(registration_form.password.data)
        # return redirect(url_for('login'))
    return render_template('registration.html', form=registration_form)


if __name__ == '__main__':
    app.secret_key=b'_5#y2L"4Q8z178s/\\n\xec]/'
    app.run(host='127.0.0.1', port=8080, debug=True)
