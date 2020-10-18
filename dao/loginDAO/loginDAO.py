import string,random
from mailing import *
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
from dao.uniqueDAO.uniqueDAO import uniqueDAO
import math


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class loginDAO:

    def __init__(self,mysql):
        self.mysql = mysql
        self.cartDAO = cartDAO(mysql)
        self.unikDAO = uniqueDAO(mysql)

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
                            self.cartDAO.retrieve_cart_items(iduser),
                            result['lockout_start'])
                            
            if not result:
                return None
            return u
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while retrieving user in "+__name__+":" +str(e))
            return None

    def get_user_by_email(self,email):
        query = "SELECT * FROM user WHERE iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (email,))
            result = cur.fetchone()
            result['addr_info'] = self.getAddr(result['email'])
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
                            self.getAddr(email),
                            self.cartDAO.retrieve_cart_items(email))
                            
            if not result:
                return None
            return u
        except Exception as e:
            logger.error("User "+str(email)+ " encountered an error while retrieving user by email in "+__name__+":" +str(e))
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

    #Return string 
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
            dtdiff = math.fabs((datetime.now() - result['lockout_start']).total_seconds())/60
            if dtdiff < DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES:
                return "Your account has been locked out. Please wait for another {:.0f} min".format(DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES-dtdiff)

            # Account lockout permenant until reset password
            # if u.incorrectLoginCount>=5:
            #     return "Your account has been locked. Please check your email for a reset link."

            if password_validator(password, result['password']):
                logger.info(email + " just logged in")
                self.increase_fail_login_count(u.iduser,0)
                self.unikDAO.delete_unik_by_iduser(u.iduser)
                return u
            else:
                #FAILURE TO LOGIN
                logger.info(email + " failed to login for the {} time".format(u.incorrectLoginCount+1))
                self.increase_fail_login_count(u.iduser)

                # Lockout for X minutes if login count>=3
                if u.incorrectLoginCount>=2:
                    self.increase_fail_login_count(u.iduser,0)
                    self.insert_lockout_start(u.iduser)
                    return "Your account has been locked out. Please wait for another {:.0f} min".format(DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES)



                #If continuous logout count reaches 5, send reset email
                # if u.incorrectLoginCount>=4:
                #     unik=self.get_random_string(45)
                #     self.unikDAO.delete_unik_by_iduser(u.iduser)
                #     self.unikDAO.insert_unik(u.iduser,unik,"password")
                #     send_reset_pw_email("http://"+str(DefaultConfig.SERVER_IP)+":"+str(DefaultConfig.SERVER_PORT)+"/reset/password/"+unik,u.email)
                #     return "Your account has been locked. Please check your email for a reset link."
                
                return None
        except Exception as e:
            logger.error("User "+str(email)+ " encountered an error while checking for valid login in "+__name__+":" +str(e))
            return None

    def request_reset_pw_email(self,iduser,email):
        unik=self.get_random_string(45)
        self.unikDAO.delete_unik_by_iduser(iduser)
        self.unikDAO.insert_unik(iduser,unik,"password")
        send_reset_pw_email("http://"+str(DefaultConfig.SERVER_IP)+":"+str(DefaultConfig.SERVER_PORT)+"/reset/password/"+unik,email)
        return True

    def increase_fail_login_count(self,iduser,count_to_set=-1):
        if count_to_set==-1:
            query = "update user set incorrect_login_count = incorrect_login_count+1 where iduser = %s"
            var_tuple = (iduser,)
        elif count_to_set>=0:
            query = "update user set incorrect_login_count = %s where iduser = %s"
            var_tuple = (count_to_set,iduser)

        try:
            cur = self.mysql.connection.cursor()
            result = cur.execute(query,var_tuple)
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

    def insert_lockout_start(self,iduser):
        query="update user set lockout_start = %s where iduser=%s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query,(datetime.now(),iduser))
            self.mysql.connection.commit()
            logger.info("User {} recorded a lockout timer start.".format(iduser))
            return True
        except Exception as e:
            logger.error("User {} encountered error when inserting last login attempt in {}".format(iduser,__name__))
            return False

    def date_test(self):
        query_select = "SELECT lockout_start FROM user where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query_select,(2,))
            result = cur.fetchone()
            a = result['lockout_start']-datetime.now()
            print("This is microseconds {} and this is entire. {} minutes".format(a,math.fabs(a.total_seconds()/60)))
            return True
        except Exception as e:
            print(e)
            # logger.error("User "+str(iduser)+ " encountered an error while checking if is new login in "+__name__+":" +str(e))
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

    def get_address_by_id(self,iduser):
        query = "select * from address where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query,(iduser,))
            result = cur.fetchone()
            logger.info("User "+str(iduser)+" retrieved their address")
            return result if result else None
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while getting address in "+__name__+":" +str(e))
            return None


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

    def update_pw_change_date(self,iduser):
        query = "update user set password_change_date = %s where iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query,(datetime.now(),iduser))
            self.mysql.connection.commit()
            return True
            
        except Exception as e:
            logger.warning("User {} encountered an error while updating password change date".format(iduser,__name__))
            return None

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
            self.update_pw_change_date(iduser)

            logger.info("User "+str(iduser)+" updated their password")
            return True,"Successfully updated"
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating password in "+__name__+":" +str(e))
            return None,"system error"

    

    def update_pw_from_unik(self,uniqueString,newPassword):
        query = "update user set password = %s ,incorrect_login_count=0,password_change_date=%s\
            where iduser in (select fk_iduser from unique_link where idunique_link = %s)"
        query_delete = "delete from unique_link where idunique_link =  %s"
        try:
            cur = self.mysql.connection.cursor()
            result = cur.execute(query,(encrypt_password(newPassword),datetime.now(),uniqueString))
            result = cur.execute(query_delete,(uniqueString,))
            self.unikDAO.delete_unik_by_string(uniqueString)
            self.mysql.connection.commit()
            return True if result else None
        except Exception as e:
            logger.warning("encountered an error while updating password from unique string in "+__name__+":" +str(e))
            return None

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

    def get_random_string(self,length):
        letters = string.ascii_lowercase
        result_str = ''.join(random.choice(letters) for i in range(length))
        return result_str