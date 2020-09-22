from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_login import LoginManager
from flask_mysqldb import MySQL

from flask_wtf import CSRFProtect,FlaskForm
from wtforms import StringField,FileField,DecimalField
import logging
from models import User
import re
from appConfig import DefaultConfig
from db_helper import db_helper
from wtform import *

app = Flask(__name__, template_folder="templates")

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

# csrf = CSRFProtect(app)
app.config.from_object(DefaultConfig)
# login = LoginManager(app)
# tesitng
mysql = MySQL(app)
dbh = db_helper(mysql)

server = "dev"
# server = "prod"
if server=="dev":
    ip = "127.0.0.1"
    port = "8080"

if server=="prod":
    ip="0.0.0.0"
    port="3389"
src = "http://"+ip+":"+port+"/"


logger = logging.getLogger(__name__)
fh = logging.FileHandler('sys.log')
sh = logging.StreamHandler()
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)
logger.addHandler(sh)
logger.setLevel(logging.INFO)

logging.basicConfig(filename="server.log",level=logging.INFO,
                format="%(asctime)s - %(levelname)s - %(message)s")


class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")



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
        login_result = dbh.check_login(login_form.username.data,
                                   login_form.password.data)
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
    fname = registration_form.firstName.data
    lname = registration_form.lastName.data
    email = registration_form.email.data
    password = registration_form.password.data
    passwordConfirm = registration_form.confirmPassword.data
    successFlag = True
    tab = "reg"
    if registration_form.validate_on_submit():
        nameRegex = "(^[\w\s]{1,}[\w\s]{1,}$)"
        namePat = re.compile(nameRegex)
        emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        emailPat = re.compile(emailRegex)
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        email_matched = re.search(emailPat, email)
        fname_matched=re.search(namePat,fname)
        lname_matched=re.search(namePat,lname)
        password_matched = re.search(
            passwordPat, password)
        if not email_matched:
            flash('Please enter a valid email', 'register')
            successFlag=False
            logger.warning("email failed regex")
        if password != passwordConfirm:
            flash('Please enter the same password for both fields', 'register')
            logger.warning("password don't match")
            successFlag=False
        else:
            if not password_matched:
                logger.warning("Password doesn't satisfy criteria")
                successFlag=False
                flash('Password must contain minimum 8 characters, with 1 uppercase, 1 lowercase, 1 digit & 1 special char', 'register')

        if dbh.email_exist(email):
            successFlag=False
            flash('Email Already Exist','register')
            logger.info("Register failed because "+email+" already exist")

        if not fname_matched or not lname_matched:
            successFlag=False
            logger.info("Firstname or lastname needs to be legitimate.")

        
        if successFlag:
            user = User(fname,lname,email,password)
            logger.info("Information sufficient to register.")
            dbh.signup(user)
            tab="log"
    else:
        logger.info("Not validate on submit")
    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src, tab=tab)


@ app.route("/sell/publish_listing", methods=['POST'])
def publish():
    # need to check file type and probably do a file scan
    # files = request.form.getlist("files")
    files = request.files.getlist("files")
    print(files)
    logger.info("Somebody just published a listing of "+str(len(files))+" pictures")
    return render_template('landing.html')


@ app.route('/sell/dashboard')
def sell_dashboard():
    dashboard={}
    
    dashboard["lifetime_revenue"] = str.format("${:,.2f}",67876.90)
    dashboard["wallet_amt"] = str.format("${:,.2f}",273.00)
    dashboard["star_rating_avg"] = 4.7
    return render_template('sell/sell_dashboard.html',dashboard = dashboard)


@ app.route('/products/checkout')
def checkout():
    td = {}
    td["Product1"]={"name":"Chia Seeds", "price":28, "quantity":3}
    td["Product2"]={"name":"Apple", "price":28.2, "quantity":4}

    total = 0.0
    for v in td.values():
        total +=(v["price"]*v["quantity"])

    return render_template('products/checkout.html',checkout_total = total,dict = td)


if __name__ == '__main__':
    app.secret_key=b'_5#y2L"4Q8z178s/\\n\xec]/'
    app.run(host=ip, port=port, debug=True)

