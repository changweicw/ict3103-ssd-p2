from datetime import datetime
from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
import models
from dao.cartDAO.cartDAO import cartDAO


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class loginDAO:

    def __init__(self,mysql):
        self.mysql = mysql
        self.cartDAO = cartDAO(mysql)
    def getUser(self,iduser):
        query = "SELECT * FROM user WHERE iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (iduser,))
            result = cur.fetchone()
            result['addr_info'] = self.getAddr(iduser)
            u = models.User(result['fname'],
                            result['lname'],
                            result['email'], 
                            result['password'],
                            result['total_revenue'],
                            result['rating_avg'],
                            result['password_change_date'],
                            result['incorrect_login_count'],
                            result['user_join_date'],
                            result['removed'],
                            result['iduser'],
                            self.getAddr(iduser),
                            self.cartDAO.retrieve_cart_items(iduser))
                            
            if not result:
                return None
            return u
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while retrieving user in "+__name__+":" +str(e))
            return None

    def getAddr(self,iduser):
        query="Select * from address where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (iduser,))
            result = cur.fetchone()
            return result or None
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while retrieving address in "+__name__+":" +str(e))
            return None

    def check_login(self, email, password):
        query = "SELECT * FROM user WHERE email = %s"
        try:
            cur = self.mysql.connection.cursor()
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
                self.increase_fail_login_count(u.iduser)
                return None
        except Exception as e:
            logger.error("User "+str(email)+ " encountered an error while checking for valid login in "+__name__+":" +str(e))
            return None

    def increase_fail_login_count(self,iduser):
        query = "update user set incorrect_login_count = incorrect_login_count+1 where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            result = cur.execute(query,(iduser,))
            self.mysql.connection.commit()
            print(result)
            return True
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while increasing fail login count in "+__name__+":" +str(e))
            return None

    def email_exist(self, email):
        query_checkemail = "SELECT * from user where email = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_checkemail, (email,))
            result = cur.fetchone()
            if result is not None:
                logger.info(email+" already exist")
                return True
        except Exception as e:
            logger.error("encountered an error while checking if email exist in "+__name__+":" +str(e))
        
        return None

    def signup(self, user):
        query_insert = "INSERT INTO user (fname,lname,email,password,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            enPass = encrypt_password(user.password)
            print("Password Checker: " + enPass)
            cur.execute(query_insert, (user.fname, user.lname, user.email, enPass, user.total_revenue,
                                       user.rating, user.passwordChangeDate, user.incorrectLoginCount, user.userJoinDate, user.removed))
            self.mysql.connection.commit()
            logger.info("Register successful for "+user.fname)

            return True
        except Exception as e:
            logger.error("User "+str(user.iduser)+ " encountered an error while sign-ing up in "+__name__+":" +str(e))
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
            logger.error("User "+str(iduser)+ " encountered an error while checking if is new login in "+__name__+":" +str(e))
            return None
    
    def insert_login_history(self,iduser,ipaddress):
        query_insert = "INSERT INTO login_origin_history VALUES (%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_insert,(iduser,ipaddress))
            self.mysql.connection.commit()
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while inserting login history in "+__name__+":" +str(e))
            return False


    def update_email(self,iduser,email):
        query_insert = "update user set email = %s where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_insert,(email,iduser))
            self.mysql.connection.commit()
            logger.info("User "+str(iduser)+" updated their email")
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating email in "+__name__+":" +str(e))
            return False

    def update_address(self,iduser,address):
        query = "update address set address_line = %s, unit_no=%s, zipcode=%s where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query,(address['line'],address['unitno'],address['zipcode'],iduser))
            self.mysql.connection.commit()
            logger.info("User "+str(iduser)+" updated their address")
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating address in "+__name__+":" +str(e))
            return False

    def update_pw(self,iduser,currentpw,newpw):
        query_select = "select * from user where iduser = %s"
        query_update = "update user set password = %s where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_select,(iduser,))
            user = cur.fetchone()
            if not password_validator(currentpw,user['password']):
                logger.warning("User "+str(iduser)+" tried to change their password with a wrong current password")
                return None,"wrong current password"

            pw_hist = self.retrieve_pw_history(iduser)
            if len(pw_hist)>5:
                self.delete_one_earliest_pw_history(iduser)
                pw_hist = self.retrieve_pw_history(iduser)
                
            for x in pw_hist:
                if password_validator(newpw,x['password']):
                    logger.warning("User "+str(iduser)+" tried to change their password to a history password")
                    return None,"new password is one of your previous 5 passwords"
            cur.execute(query_update,(encrypt_password(newpw),iduser))
            self.mysql.connection.commit()
            self.insert_pw_history(iduser,newpw)
            logger.info("User "+str(iduser)+" updated their password")
            return True,"Successfully updated"
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating password in "+__name__+":" +str(e))
            return None,"system error"
        
    def retrieve_pw_history(self,iduser):
        query = "select * from pw_history where fK_iduser = %s order by date_changed desc"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query,(iduser,))
            return cur.fetchall()
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while checking password history in "+__name__+":" +str(e))
            return None

    def insert_pw_history(self,iduser,pw):
        query = "insert into pw_history (fk_iduser,password,date_changed) values (%s,%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            result = cur.execute(query,(iduser,encrypt_password(pw),datetime.now()))
            self.mysql.connection.commit()
            return True if result else None
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while inserting password history in "+__name__+":" +str(e))
            return None

    def delete_one_earliest_pw_history(self,iduser):
        query_delete = "delete from pw_history where fk_iduser = %s order by date_changed asc limit 1"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_delete,(iduser,))
            self.mysql.connection.commit()
            return True
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while deleting password history in "+__name__+":" +str(e))
            return None