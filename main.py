from flask import Flask, render_template, redirect, url_for, flash, session, request, jsonify, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_mysqldb import MySQL
from flask_wtf import CSRFProtect, FlaskForm
from flask_wtf.csrf import CSRFError
from wtforms import StringField, FileField, DecimalField
from werkzeug.utils import secure_filename
from models import User, Product_listing
from appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from dao.productDAO.productDAO import productDAO
from dao.cartDAO.cartDAO import cartDAO
from dao.uniqueDAO.uniqueDAO import uniqueDAO
from dao.transactionDAO.transactionDAO import transactionDAO
from wtform import *
from google.cloud import storage
from cloudstore_utils import cloudstore_utils as csutils
from mailing import *
from log_helper import *
from base64 import b64decode
from datetime import datetime, timedelta

import string
import random
import logging
import os
import re
import uuid
import ipaddress
import platform


app = Flask(__name__, template_folder="templates")

# ========================================
# Flask WTF CSRF Protection
# ========================================
csrf = CSRFProtect()
csrf.init_app(app)

# ========================================
# Flask Login Manager
# ========================================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_message = "Please login first."

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.permanent_session_lifetime = timedelta(
    minutes=int(DefaultConfig.SESSION_TIMEOUT))

# ========================================
# DATABASE
# ========================================
app.config.from_object(DefaultConfig)
mysql = MySQL(app)
loginDAO = loginDAO(mysql)
productDAO = productDAO(mysql)
cartDAO = cartDAO(mysql)
unikDAO = uniqueDAO(mysql)
transactionDAO = transactionDAO(mysql)

# ========================================
# GOOGLE BUCKET INIT
# ========================================
csu = csutils()
ALLOWED_EXTENSIONS = DefaultConfig.ALLOWED_EXTENSIONS

# ========================================
# SERVER ENV
# ========================================

# server = "dev"
# server = "prod"
# if server == "dev":
# ip = "0.0.0.0"
# ip = "127.0.0.1"
# port = app.config['SERVER_PORT']
# port = "8000"

ip = "0.0.0.0"
# ip = "127.0.0.1"
port = app.config['SERVER_PORT']
# port = "8000"


src = "http://"+ip+":"+port+"/"

# ========================================
# LOGGER SETUPS
# ========================================
logger = prepareLogger(__name__, 'sys.log', logging.Formatter(
    '%(ip)s - %(asctime)s - %(levelname)s - %(message)s'))

# ROOT LEVEL LOG
logging.basicConfig(filename=DefaultConfig.LOGGING_FOLDER+"/server.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ========================================
# FLASK FORMS
# ========================================


class publishForm(FlaskForm):
    title = StringField("title")
    desc = StringField("desc")
    price = DecimalField("price")
    files = FileField("files")

# @app.before_request
# def logIp():
#     # logger.info("Accessed the page login with wrong password", extra={'ip': request.remote_addr})
#     print(request)


@app.route('/')
def landing():
    session['title'] = "Collaboratory Mall"
    # print(dbh.retrieve_all_products())
    # loginDAO.date_test()
    # print(str(ipaddress.IPv4Address(int(ipaddress.IPv4Address(request.remote_addr)))))
    products = productDAO.retrieve_all_products()
    cartItems = []
    cartTotal = 0.0
    if current_user.is_authenticated:
        cartItems = cartDAO.retrieve_cart_items(current_user.iduser)
        for item in cartItems:
            cartTotal = cartTotal + (item['price'] * item['qty'])
    # transactionDAO.insert_transaction(2)
    # sendLoginEmail("Raphael","raphaelisme@gmail.com")
    return render_template('landing.html', products=products, cartItems=cartItems)
    # sendLoginEmail("Raphael","raphaelisme@gmail.com")
    # return render_template('landing.html',products=products)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('account/my-account.html')


@app.route('/account/update', methods=['POST'])
def account_update():
    j = request.get_json()
    ret_email = False
    ret_add = False
    retString = ""
    if not current_user.is_authenticated:
        return {'msg': "You need to be logged in first"}, 400

    if 'email' in j:
        ret_email = loginDAO.update_email(current_user.iduser, j['email'])
        retString = retString + "Error saving email" if not ret_email else ""

    if 'address' in j:
        ret_add = loginDAO.update_address(current_user.iduser, j['address'])
        retString = retString + "Error saving address" if not ret_add else ""

    if 'currentpw' in j and 'newpw' in j:
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        pw_match = re.search(passwordPat, j['newpw'])
        if not pw_match:
            retString = "Password must contain minimum 8 characters, with 1 uppercase, 1 lowercase, 1 digit & 1 special char"
        else:
            ret_pw_status, msg = loginDAO.update_pw(
                current_user.iduser, j['currentpw'], j['newpw'])
            retString = retString + msg if not ret_pw_status else ""
    return {'msg': retString}, 200 if retString == "" else 400


@app.route('/login', methods=['GET', 'POST'])
def login_landing():
    if current_user.is_authenticated:
        return redirect(url_for('landing'))
    login_form = LoginForm()
    ip_source = ipaddress.IPv4Address(request.remote_addr)
    registration_form = RegistrationForm()
    if 'src' in request.args:
        session['src'] = request.args["src"]
    if login_form.validate_on_submit():
        remember_me = True if 'remember_me' in request.form and request.form[
            'remember_me'] == 'on' else False
        login_result = loginDAO.check_login(login_form.username.data,
                                            login_form.password.data)
        if isinstance(login_result, str):
            flash(login_result, 'login')
            logger.warning(login_form.username.data +
                           " Attempted login failed", extra={'ip': request.remote_addr})
        elif login_result:
            # Handle Redirect after login success
            login_user(login_result, remember=remember_me, duration=timedelta(
                days=int(app.config['REMEMBER_ME_TIMEOUT_DAYS'])))
            if loginDAO.is_new_login(login_result.iduser, int(ip_source)):
                sendLoginEmail(ip_source, login_result.email)

                # Redirect to landing page
            logger.info(login_form.username.data+" Successfully logged in.",
                        extra={'ip': request.remote_addr})
            return redirect(session['src'] if 'src' in session else url_for('landing'))
        else:
            logger.warning(login_form.username.data +
                           " Tried to login with wrong password", extra={'ip': request.remote_addr})
            flash(
                'Your username or password is incorrect or you do not have an account with us.', 'login')

    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src)

@app.route('/initiate_reset_pw',methods=['POST','GET'])
def init_reset_pw():
    return render_template('account/init-reset-pw.html',form=resetForm())

@app.route("/reset_password_email",methods=['POST'])
def send_reset_email():
    unik=get_random_string(45)
    email = request.form.get("email")
    user = loginDAO.get_user_by_email(email)
    unikDAO.delete_unik_by_iduser(user.iduser)
    unikDAO.insert_unik(user.iduser,unik,"password")
    # print("{}-{}-{}-{}".format(DefaultConfig.SERVER_IP,DefaultConfig.SERVER_PORT,unik,email))
    send_reset_pw_email("http://"+str(DefaultConfig.SERVER_IP)+":"+str(DefaultConfig.SERVER_PORT)+"/reset/password/"+unik,email)
    return redirect(url_for('login_landing'))

@app.route("/register", methods=['GET', 'POST'])
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
    iziMsg = "Not successful"
    if registration_form.validate_on_submit():
        if isCommonPassword(password):
            flash('This is a common password. Please use a new one.', 'register')
            successFlag = False
            logger.warning(email+" tried to register with a common password.",
                           extra={'ip': request.remote_addr})
        nameRegex = "(^[\w\s]{1,}[\w\s]{1,}$)"
        namePat = re.compile(nameRegex)
        emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
        emailPat = re.compile(emailRegex)
        passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
        passwordPat = re.compile(passwordRegex)
        email_matched = re.search(emailPat, email)
        fname_matched = re.search(namePat, fname)
        lname_matched = re.search(namePat, lname)
        password_matched = re.search(
            passwordPat, password)
        if not email_matched:
            flash('Please enter a valid email', 'register')
            successFlag = False
            logger.warning("email failed regex", extra={
                           'ip': request.remote_addr})
        if password != passwordConfirm:
            flash('Please enter the same password for both fields', 'register')
            logger.warning("password don't match", extra={
                           'ip': request.remote_addr})
            successFlag = False
        else:
            if not password_matched:
                logger.warning("Password doesn't satisfy criteria",
                               extra={'ip': request.remote_addr})
                successFlag = False
                flash('Password must contain minimum 8 characters, with 1 uppercase, 1 lowercase, 1 digit & 1 special char', 'register')

        if loginDAO.email_exist(email):
            successFlag = False
            flash('Email Already Exist', 'register')
            logger.info("Register failed because "+email +
                        " already exist", extra={'ip': request.remote_addr})

        if not fname_matched or not lname_matched:
            successFlag = False
            logger.info("Firstname or lastname needs to be legitimate.", extra={
                        'ip': request.remote_addr})
            flash('First Name or last name might not be legitimate.', 'register')

        if successFlag:
            user = User(fname, lname, email, password)
            logger.info("Information sufficient to register.",
                        extra={'ip': request.remote_addr})
            loginDAO.signup(user)
            tab = "log"
            iziMsg = "Account Successfully created!"
    else:
        logger.info("Not validate on submit", extra={
                    'ip': request.remote_addr})
    return render_template('account/login.html', form=login_form, reg_form=registration_form, src=src, tab=tab, iziMsg=iziMsg)


@app.route("/reset/sendEmail", methods=['post'])
@login_required
def reset_pw_send_email():
    result = loginDAO.request_reset_pw_email(
        current_user.iduser, current_user.email)
    if result:
        return {'msg': 'Email sent to '+current_user.email}, 200
    else:
        return {'msg': 'Error requesting for email.'}, 400


@app.route('/reset/password/<unik>')
def reset_pw_link(unik):
    ret = unikDAO.search_unik(unik)
    if ret:
        retMsg = ret['idunique_link']
        return render_template('account/reset_password_landing.html', unik=unik)
    else:
        retMsg = "No unique link found"
    return {'msg': retMsg}, 200


@app.route('/account/update_password_reset', methods=['POST'])
def reset_pw():
    # unik=request.form['unik']
    j = request.get_json()
    uniqueString = j['unik']
    newPassword = j['newpw']
    passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
    passwordPat = re.compile(passwordRegex)
    pw_match = re.search(passwordPat, newPassword)
    if pw_match:
        result = loginDAO.update_pw_from_unik(uniqueString, newPassword)
        if result:
            msg = "Password updated!"
            return {'msg': msg}, 200
    else:
        msg = "Please ensure your password is a minimum of 8 characters, contain 1 upper case, 1 lower case, and a special character."
        return {'msg': msg}, 400
    msg = "Link expired or system error!"
    return {'msg': msg}, 400


@app.route('/cart/addToCart', methods=['POST'])
def addtocart():
    j = request.get_json()
    if 'idproduct' not in j or 'qty' not in j:
        retdata = {'msg': 'Incorrect fields'}
        return retdata, 400
        # return Response("Not found",status=200)

    if not str(j['idproduct']).isnumeric() or not str(j['qty']).isnumeric():
        retdata = {'msg': 'Incorrect fields'}
        return retdata, 400

    productid = j['idproduct']
    quantity = j['qty']
    userid = current_user.iduser if current_user.is_authenticated else -1

    if userid == -1:
        retdata = {'msg': 'You need to be logged in.'}
        return retdata, 400

    if cartDAO.add_to_cart(userid, productid, quantity) > 0:
        retdata = {'msg': 'Successfully added to cart.'}
        return retdata, 200
    else:
        logger.warning("Attempted to add to cart but 0 rows updated.", extra={
                       'ip': request.remote_addr})
        retdata = {'msg': 'Not added to cart.'}
        return retdata, 400

# @app.route('/cart/updateCartQty',methods=['POST'])
# def updatecartqty():
#     j = request.get_json()
#     if 'idproduct' not in j or 'qty' not in j:
#         retdata = {'msg':'Not added to cart.'}
#         return retdata,400

#     if not str(j['idproduct']).isnumeric() or not str(j['qty']).isnumeric():
#         retdata = {'msg':'Not added to cart.'}
#         return retdata,400

#     productid = j['idproduct']
#     quantity = j['qty'] if j['qty']>=0 else 0
#     userid = current_user.iduser if current_user.is_authenticated else -1

#     if userid == -1:
#         retdata = {'msg':'You need to be logged in.'}
#         return retdata,400

#     if cartDAO.update_cart_qty(userid,productid,quantity)>0:
#         retdata = {'msg':'Updated cart!'}
#         return retdata,200
#     else:
#         logger.warning("Attempted to add to cart but 0 rows updated.")
#         retdata = {'msg':'Not added to cart.'}
#         return retdata,400


@app.route("/sell/publish_listing", methods=['POST'])
@login_required
def publish():
    # need to check file type and probably do a file scan
    # files = request.form.getlist("files")
    j = request.get_json()
    files = j['imageList']
    title = j["title"]
    desc = j["desc"]
    price = j["price"]
    if not isinstance(title, str) or not isinstance(desc, str) or not isinstance(price, str):
        return jsonify(success=False)
    urlList = []
    logger.info("Title:"+title+".Desc:"+desc+".Price:" +
                price, extra={'ip': request.remote_addr})
    logger.info("Somebody is going to pubilish a listing with " +
                str(len(files))+" pictures", extra={'ip': request.remote_addr})
    for f in files:
        if f.split(';')[0].split('/')[1] not in app.config['ALLOWED_EXTENSIONS'] or (len(f.split(',')[1]) - 814)/1.37 / 1024 > 1024:
            return jsonify(success=False)
    # for f in files:
    #     csu.bucket_name=DefaultConfig.GOOGLE_BUCKET_ID
    #     public_url =  csu.upload_to_bucket(f)
    #     # tempSplit = str(public_url).split("/")
    #     urlList.append(public_url)
    fileList = []
    for f in files:
        fileList.append(
            {'b64': f.split(',')[1], 'file_ext': f.split(';')[0].split('/')[1]})
    urlList = csu.upload_to_bucket_b64List(fileList)

    # tempProd = Product_listing(title,desc,urlList,price,0) eventually replace the last 0 with iduser
    tempProd = Product_listing(
        title, desc, urlList, price, current_user.iduser, False, 100)
    idprod = productDAO.publish_listing(tempProd)
    if idprod:
        logger.info(str(current_user.iduser)+":"+current_user.fname +
                    " has just published a product with id: "+str(idprod), extra={'ip': request.remote_addr})
    else:
        logger.warning(str(current_user.iduser)+" publish failed",
                       extra={'ip': request.remote_addr})

    # dbh.upload_to_bucket(files[0].filename)
    return jsonify(success=True)


@app.route('/sell/dashboard')
@login_required
def sell_dashboard():
    dashboard = {}

    dashboard["lifetime_revenue"] = str.format("${:,.2f}", 67876.90)
    dashboard["wallet_amt"] = str.format("${:,.2f}", 273.00)
    dashboard["star_rating_avg"] = 4.7
    return render_template('sell/sell_dashboard.html', dashboard=dashboard)


@app.route('/products/checkout')
@login_required
def checkout():
    ship_fee = 7
    cart = []
    cartItems = cartDAO.retrieve_cart_items(current_user.iduser)
    if len(cartItems) <= 0:
        return redirect('/')
    # calculating total price
    total = round(sum([x['price']*x['qty'] for x in cartItems]) + ship_fee, 2)
    for x in cartItems:
        cart.append(
            {"name": x['name'], "price": x['price'], "quantity": x['qty']})

    return render_template('products/checkout.html', checkout_total=total, cartItems=cart, shipping=ship_fee)


@app.route('/products/<randomString>/after_pay')
@login_required
def after_pay(randomString):
    print(randomString)
    res = transactionDAO.insert_transaction(current_user.iduser, randomString)
    del_res = cartDAO.empty_cart(current_user.iduser)
    retmsg = "Thank you for purchasing!"
    if not res:
        logger.error("User {} attempted inserting transaction after paying, but not recorded ".format(
            current_user.iduser))
    else:
        print(res)
    return redirect('/')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('landing'))


@login_manager.user_loader
def load_user(iduser):
    return loginDAO.getUser(iduser)


@login_manager.unauthorized_handler
def getout():
    x = request
    return redirect(url_for('login_landing', src=x.base_url))


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return {'msg': "Don't be a bad user. Give me a proper CSRF Token."}, 400


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def isCommonPassword(password):
    f = open(app.config['PASSWORD_COMMON_FILENAME'], "r")
    for x in f:
        if password in x:
            return True
    return False


if __name__ == '__main__':
    app.secret_key = b'_5#y2L"4Q8z178s/\\n\xec]/'
    app.run(host=ip, port=port, debug=True)
