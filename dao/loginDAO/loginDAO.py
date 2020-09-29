from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
import models


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class loginDAO:

    def __init__(self,mysql):
        self.mysql = mysql

    def getUser(self,iduser):
        query = "SELECT * FROM user WHERE iduser = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query, (iduser,))
            result = cur.fetchone()
            u = models.User(result['fname'],result['lname'],result['email'], 
            result['password'],result['total_revenue'],result['rating_avg'],result['password_change_date'],result['incorrect_login_count'],result['user_join_date'],result['removed'],result['iduser'])
            if not result:
                return None
            return u
        except Exception as e:
            return None

    def check_login(self, email, password):
        query = "SELECT * FROM user WHERE email = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query, (email,))
            result = cur.fetchone()
            if not result:
                return None

            u = models.User(result['fname'],result['lname'],result['email'], 
            result['password'],result['total_revenue'],result['rating_avg'],result['password_change_date'],result['incorrect_login_count'],result['user_join_date'],result['removed'],result['iduser'])
            

            if password_validator(password, result['password']):
                logger.info(email + " just logged in")
                return u
            else:
                logger.info(email + " failed to login")
                return None
        except Exception as e:
            logger.error(e)
            return None
       

    def email_exist(self, email):
        query_checkemail = "SELECT * from user where email = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_checkemail, (email,))
            result = cur.fetchone()
            if result is not None:
                logger.info(email+" already exist")
                return True
        except Exception as e:
            logger.error(e)
        
        return None

    def signup(self, user):
        query_insert = "INSERT INTO user (fname,lname,email,password,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        try:
            enPass = encrypt_password(user.password)
            print("Password Checker: " + enPass)
            cur.execute(query_insert, (user.fname, user.lname, user.email, enPass, user.total_revenue,
                                       user.rating, user.passwordChangeDate, user.incorrectLoginCount, user.userJoinDate, user.removed))
            self.mysql.connection.commit()
            logger.info("Register successful for "+user.fname)

            return True
        except Exception as e:
            logger.error(e)
            return None

    

    def is_new_login(self,iduser,ipaddress):
        query_select = "SELECT * FROM login_origin_history where iduser = %s and ip_address = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_select,(iduser,ipaddress))
            result = cur.fetchone()
            logger.info("Retrieved login_history of userid: "+str(iduser))
            if not result:
                self.insert_login_history(iduser,ipaddress)
                return True
            return False
        except Exception as e:
            return None
    
    def insert_login_history(self,iduser,ipaddress):
        query_insert = "INSERT INTO login_origin_history VALUES (%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_insert,(iduser,ipaddress))
            self.mysql.connection.commit()
            return True
        except Exception as e:
            logger.error(e)
            return False