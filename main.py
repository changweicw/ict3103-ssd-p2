from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect,FlaskForm
from wtforms import StringField,FileField,DecimalField
import logging

import re

from appConfig import DefaultConfig

import wtform_validator as forms

app = Flask(__name__,template_folder="templates")

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
# login = LoginManager(app)
mysql = MySQL(app)

src = "http://127.0.0.1:8080/"

logging.basicConfig(filename="system.log",
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")

@app.route('/')
def landing():
    session['title'] = "Collaboratory Mall"
    return render_template('landing.html')

@app.route('/account',methods=['GET','POST'])
def account():
    return render_template('account/my-account.html')


@app.route('/login', methods=['GET', 'POST'])
def login_landing():
    # login_form = forms.LoginForm()
    return render_template('account/login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = forms.LoginForm()
    # if login_form.validate_on_submit():
    #     # res = log_con.verify_login(
    #     #     mysql, login_form.username.data, login_form.password.data)
    #     # print(res)
    #     flash(login_form.password.data)

    return render_template('logins/account_page.html', form=login_form, src=src)

# This to be completed. 
@app.route("/sell/publish_listing", methods=['POST'])
def publish():
    # files = request.form.getlist("files")
    files = request.files.getlist("files")
    print(files)
    logging.debug("Somebody just published a listing of"+str(len(files)))
    return render_template('landing.html')

@app.route('/sell/dashboard')
def sell_dashboard():
    dashboard={}
    dashadsad = {}
    dashboard["lifetime_revenue"] = str.format("${:,.2f}",67876.90)
    dashboard["wallet_amt"] = str.format("${:,.2f}",273.00)
    dashboard["star_rating_avg"] = 4.7
    return render_template('sell/sell_dashboard.html',dashboard = dashboard)

@app.route('/products/checkout')
def checkout():
    
    td = {}
    td["Product1"]={"name":"Chia Seeds", "price":28, "quantity":3}
    td["Product2"]={"name":"Apple", "price":28.2, "quantity":4}

    total = 0.0
    for v in td.values():
        total +=(v["price"]*v["quantity"])

    return render_template('products/checkout.html',checkout_total = total,dict = td)

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
    app.secret_key=b'_5#y2L"4Q8z178s/\\n\xec]/'
    # app.run(host='0.0.0.0', port=3389, debug=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
