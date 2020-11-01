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

    def __init__(self):
        self.cartDAO = cartDAO()
        self.unikDAO = uniqueDAO()

    # ------------------------------------------ 
    # Retrieve user 
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id to retrieve]
    #   #2 - [invalid user id]
    # ------------------------------------------
    # Returns 
    #   [False]         if failed
    #   [user object]   if successful
    # ------------------------------------------
    def getUser(self,iduser,conn=None):
        query = "SELECT * FROM user WHERE iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query, (iduser,))
            result = cur.fetchone()
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
                            self.getAddr(iduser,conn),
                            self.cartDAO.retrieve_cart_items(iduser,conn),
                            result['lockout_start'])
                            
            if not result:
                return None
            return u
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while retrieving user in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Retrieve user by email
    # ------------------------------------------
    # test inputs: 
    #   #1 - [email of user to retrieve]
    #   #2 - [invalid email]
    # ------------------------------------------
    # Returns 
    #   [False]         if failed
    #   [user object]   if successful
    # ------------------------------------------
    def get_user_by_email(self,email,conn=None):
        query = "SELECT * FROM user WHERE email = %s"
        try:
            cur = conn.cursor()
            cur.execute(query, (email,))
            result = cur.fetchone()
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
                            self.getAddr(email,conn),
                            self.cartDAO.retrieve_cart_items(email,conn))
                            
            if not result:
                return None
            return u
        except Exception as e:
            logger.error("User "+str(email)+ " encountered an error while retrieving user by email in "+__name__+":" +str(e))
            return None
    
    # ------------------------------------------ 
    # Retrieve address of user 
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id to retrieve]
    #   #2 - [invalid user id]
    # ------------------------------------------
    # Returns 
    #   [False]           if failed
    #   [address object]  if successful, containing
    #       [address id(int)], [user id address belongs to(int)],
    #       [address line(string)], [unit num(string)], [zipcode(int)]
    # ------------------------------------------
    def getAddr(self,iduser,conn=None):
        query="Select * from address where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query, (iduser,))
            result = cur.fetchone()
            return result or None
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while retrieving address in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Check credentials before logging in
    # ------------------------------------------
    # test inputs: 
    #   #1 - [email], [password]
    #   #2 - [invalid email], [password]
    #   #3 - [email], [invalid password]
    # ------------------------------------------
    # Returns 
    #   [string err msg]    if failed
    #   [user object]       if successful
    # ------------------------------------------
    def check_login(self, email="", password="",conn=None):
        query = "SELECT * FROM user WHERE email = %s"

        try:
            cur = conn.cursor()
            cur.execute(query, (email,))
            result = cur.fetchone()
            if not result:
                return None
            print(result)
            u = models.User(result['fname'],result['lname'],result['email'], 
            result['password'],result['total_revenue'],result['rating_avg'],result['password_change_date'],result['incorrect_login_count'],result['user_join_date'],result['removed'],result['iduser'])
            
            #Calculating whether locked out or not
            dtdiff = math.fabs((datetime.now() - result['lockout_start']).total_seconds())/60
            if dtdiff < DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES:
                return "Your account has been locked out. Please wait for another {:.0f} min".format(DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES-dtdiff)

            if password_validator(password, result['password']):
                logger.info(email + " just logged in")
                self.increase_fail_login_count(u.iduser,0,conn)
                self.unikDAO.delete_unik_by_iduser(u.iduser,conn)
                print("returning")
                return u
            else:
                #FAILURE TO LOGIN
                logger.info(email + " failed to login for the {} time".format(u.incorrectLoginCount+1))
                self.increase_fail_login_count(u.iduser,conn)

                # Lockout for X minutes if login count>=3
                if u.incorrectLoginCount>=2:
                    self.increase_fail_login_count(u.iduser,0,conn)
                    self.insert_lockout_start(u.iduser,conn)
                    return "Your account has been locked out. Please wait for another {:.0f} min".format(DefaultConfig.ACCOUNT_LOCOKOUT_MINUTES)

                #If continuous logout count reaches 5, send reset email
                # if u.incorrectLoginCount>=4:
                #     unik=self.get_random_string(45)
                #     self.unikDAO.delete_unik_by_iduser(u.iduser)
                #     self.unikDAO.insert_unik(u.iduser,unik,"password")
                #     send_reset_pw_email("http://"+str(DefaultConfig.SERVER_IP)+":"+str(DefaultConfig.SERVER_PORT)+"/reset/password/"+unik,u.email)
                #     return "Your account has been locked. Please check your email for a reset link."
                
                return "Your username or password is incorrect or you do not have an account with us."
        except Exception as e:
            logger.error("User "+str(email)+ " encountered an error while checking for valid login in "+__name__+":" +str(e))
            return None

    # Not in use
    def request_reset_pw_email(self,iduser,email,conn=None):
        unik=self.get_random_string(45)
        self.unikDAO.delete_unik_by_iduser(iduser,conn)
        self.unikDAO.insert_unik(iduser,unik,"password",conn)
        send_reset_pw_email("http://"+str(DefaultConfig.SERVER_IP)+":"+str(DefaultConfig.SERVER_PORT)+"/reset/password/"+unik,email)
        return True

    # ------------------------------------------ 
    # Increasing continuous failed login count
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user to increase]
    #   #2 - [id of user to increase], [1]
    #   #3 - [invalid user id]
    #   #4 - [invalid user id], [1]
    # ------------------------------------------
    # Returns 
    #   [None]    if failed
    #   [not None]       if successful
    # ------------------------------------------
    def increase_fail_login_count(self,iduser,count_to_set=-1,conn=None):
        if count_to_set==-1:
            query = "update user set incorrect_login_count = incorrect_login_count+1 where iduser = %s"
            var_tuple = (iduser,)
        elif count_to_set>=0:
            query = "update user set incorrect_login_count = %s where iduser = %s"
            var_tuple = (count_to_set,iduser)

        try:
            cur = conn.cursor()
            result = cur.execute(query,var_tuple)
            conn.commit()
            return result
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while increasing fail login count in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Checking if email already exist in database
    # ------------------------------------------
    # test inputs: 
    #   #1 - [email]
    #   #2 - [invalid email]
    # ------------------------------------------
    # Returns 
    #   [True]  if email exist or error encountered with server
    #   [None]  if email does not exist
    # ------------------------------------------
    def email_exist(self, email,conn=None):
        query_checkemail = "SELECT * from user where email = %s"
        try:
            cur = conn.cursor()
            cur.execute(query_checkemail, (email,))
            result = cur.fetchone()
            if result is not None:
                logger.info(email+" already exist")
                return True
            return None
        except Exception as e:
            logger.error("encountered an error while checking if email exist in "+__name__+":" +str(e))
            return True

    # ------------------------------------------ 
    # Signing up a new user (inserting)
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user object]
    #   #2 - [invalid user object]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def signup(self, user,conn=None):
        query_insert = "INSERT INTO user (fname,lname,email,password,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        try:
            cur = conn.cursor()
            enPass = encrypt_password(user.password)

            cur.execute(query_insert, (user.fname, user.lname, user.email, enPass, user.total_revenue,
                                       user.rating, user.passwordChangeDate, user.incorrectLoginCount, user.userJoinDate, user.removed))
            conn.commit()
            logger.info("Register successful for "+user.fname)

            return True
        except Exception as e:
            logger.error("User "+str(user.iduser)+ " encountered an error while sign-ing up in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Starting an account lockout
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id]
    #   #2 - [invalid user id]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def insert_lockout_start(self,iduser,conn=None):
        query="update user set lockout_start = %s where iduser=%s"
        try:
            cur = conn.cursor()
            cur.execute(query,(datetime.now(),iduser))
            conn.commit()
            logger.info("User {} recorded a lockout timer start.".format(iduser))
            return True
        except Exception as e:
            logger.error("User {} encountered error when inserting last login attempt in {}".format(iduser,__name__))
            return None

    # def date_test(self):
    #     query_select = "SELECT lockout_start FROM user where iduser = %s"
    #     try:
    #         cur = conn.cursor()
    #         cur.execute(query_select,(2,))
    #         result = cur.fetchone()
    #         a = result['lockout_start']-datetime.now()
    #         print("This is microseconds {} and this is entire. {} minutes".format(a,math.fabs(a.total_seconds()/60)))
    #         return True
    #     except Exception as e:
    #         print(e)
    #         # logger.error("User "+str(iduser)+ " encountered an error while checking if is new login in "+__name__+":" +str(e))
    #         return None

    # ------------------------------------------ 
    # Checking if is new login form new IP address not in history
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id] , [ip address]
    #   #2 - [invalid user id], [ip address]
    # ------------------------------------------
    # Returns 
    #   [True]  if is a new login
    #   [None]  if its not a new login, or error in server
    # ------------------------------------------
    def is_new_login(self,iduser,ipaddress,conn=None):
        query_select = "SELECT * FROM login_origin_history where iduser = %s and ip_address = %s"
        try:
            cur = conn.cursor()
            cur.execute(query_select,(iduser,ipaddress))
            result = cur.fetchone()
            logger.info("Retrieved login_history of userid: "+str(iduser))
            if not result:
                self.insert_login_history(iduser,ipaddress,conn)
                return True
            return None
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while checking if is new login in "+__name__+":" +str(e))
            return None
    
    # ------------------------------------------ 
    # Inserting login history
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id] , [ip address]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def insert_login_history(self,iduser,ipaddress,conn=None):
        query_insert = "INSERT INTO login_origin_history VALUES (%s,%s)"
        try:
            cur = conn.cursor()
            cur.execute(query_insert,(iduser,ipaddress))
            conn.commit()
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while inserting login history in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Updating email of user
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id] , [ip address]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def update_email(self,iduser,email,conn=None):
        query_insert = "update user set email = %s where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query_insert,(email,iduser))
            conn.commit()
            logger.info("User "+str(iduser)+" updated their email")
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating email in "+__name__+":" +str(e))
            return False

    # ------------------------------------------ 
    # retrieving addres by user id
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id]
    # ------------------------------------------
    # Returns 
    #   [Address object]  if success
    #   [None]  if failed
    # ------------------------------------------
    def get_address_by_id(self,iduser,conn=None):
        query = "select * from address where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query,(iduser,))
            result = cur.fetchone()
            logger.info("User "+str(iduser)+" retrieved their address")
            return result if result else None
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while getting address in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Updating address of user
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id] , [address object]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def update_address(self,iduser,address,conn=None):
        if self.get_address_by_id(iduser,conn):
            query = "update address set address_line = %s, unit_no=%s, zipcode=%s where iduser = %s"
        else:
            query = "insert into address (address_line, unit_no, zipcode, iduser) values (%s,%s,%s,%s)"
        try:
            cur = conn.cursor()
            cur.execute(query,(address['line'],address['unitno'],address['zipcode'],iduser))
            conn.commit()
            logger.info("User "+str(iduser)+" updated their address")
            return True
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating address in "+__name__+":" +str(e))
            return None

            
    # ------------------------------------------ 
    # Updating password last changed date to now
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def update_pw_change_date(self,iduser,conn=None):
        query = "update user set password_change_date = %s where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query,(datetime.now(),iduser))
            conn.commit()
            return True
        except Exception as e:
            logger.warning("User {} encountered an error while updating password change date".format(iduser,__name__))
            return None

    # ------------------------------------------ 
    # Updating password of user
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id], [current password], [new password]
    # ------------------------------------------
    # Returns 
    #   [tuple of (True, msg string)]  if success
    #   [tuple of (None, msg string)]  if failed
    # ------------------------------------------
    def update_pw(self,iduser,currentpw,newpw,conn=None):
        query_select = "select * from user where iduser = %s"
        query_update = "update user set password = %s where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query_select,(iduser,))
            user = cur.fetchone()
            if not password_validator(currentpw,user['password']):
                logger.warning("User "+str(iduser)+" tried to change their password with a wrong current password")
                return None,"wrong current password"

            pw_hist = self.retrieve_pw_history(iduser)

            if len(pw_hist)>5:
                self.delete_one_earliest_pw_history(iduser,conn)
                pw_hist = self.retrieve_pw_history(iduser,conn)
                
            for x in pw_hist:
                if password_validator(newpw,x['password']):
                    logger.warning("User "+str(iduser)+" tried to change their password to a history password")
                    return None,"new password is one of your previous 5 passwords"
            cur.execute(query_update,(encrypt_password(newpw),iduser))
            conn.commit()
            self.insert_pw_history(iduser,newpw,conn)
            self.update_pw_change_date(iduser,conn)

            logger.info("User "+str(iduser)+" updated their password")
            return True,"Successfully updated"
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while updating password in "+__name__+":" +str(e))
            return None,"system error"

    
    # ------------------------------------------ 
    # Updating password using unique string
    # ------------------------------------------
    # test inputs: 
    #   #1 - [unqiue string], [new password]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def update_pw_from_unik(self,uniqueString,newPassword,conn=None):
        query = "update user set password = %s ,incorrect_login_count=0,password_change_date=%s\
            where iduser in (select fk_iduser from unique_link where idunique_link = %s)"
        query_delete = "delete from unique_link where idunique_link =  %s"
        try:
            cur = conn.cursor()
            result = cur.execute(query,(encrypt_password(newPassword),datetime.now(),uniqueString))
            result = cur.execute(query_delete,(uniqueString,))
            self.unikDAO.delete_unik_by_string(uniqueString,conn)
            conn.commit()
            return True if result else None
        except Exception as e:
            logger.warning("encountered an error while updating password from unique string in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # retrieving password history of user
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user to retrieve]
    # ------------------------------------------
    # Returns 
    #   [list of password history objects]  if success
    #   [None]  if failed
    # ------------------------------------------
    def retrieve_pw_history(self,iduser,conn=None):
        query = "select * from pw_history where fK_iduser = %s order by date_changed desc"
        try:
            cur = conn.cursor()
            cur.execute(query,(iduser,))
            return cur.fetchall()
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while checking password history in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # inserting password history of user
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user to retrieve], [pw]
    # ------------------------------------------
    # Returns 
    #   [not None]  if success
    #   [None]      if failed
    # ------------------------------------------
    def insert_pw_history(self,iduser,pw,conn=None):
        query = "insert into pw_history (fk_iduser,password,date_changed) values (%s,%s,%s)"
        try:
            cur = conn.cursor()
            result = cur.execute(query,(iduser,encrypt_password(pw),datetime.now()))
            conn.commit()
            return True if result else None
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while inserting password history in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # deleting one earliest password history
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user to delete]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def delete_one_earliest_pw_history(self,iduser,conn=None):
        query_delete = "delete from pw_history where fk_iduser = %s order by date_changed asc limit 1"
        try:
            cur = conn.cursor()
            cur.execute(query_delete,(iduser,))
            conn.commit()
            return True
        except Exception as e:
            logger.warning("User "+str(iduser)+ " encountered an error while deleting password history in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Updating revenue
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user to update], [amount to add to revenue]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------       
    def update_revenue(self,iduser,amt,conn=None):
        query = "update user set total_revenue=total_revenue+%s where iduser = %s"
        try:
            cur = conn.cursor()
            cur.execute(query,(amt,iduser))
            conn.commit()
            return True
        except Exception as e:
            logger.error("Userid {} Error updating revenue in {}".format(iduser,__name__))
            return None

    # ------------------------------------------ 
    # Getting a random string of X length
    # ------------------------------------------
    # test inputs: 
    #   #1 - [length of string to generate]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def get_random_string(self,length):
        try:
            letters = string.ascii_lowercase
            result_str = ''.join(random.choice(letters) for i in range(length))
            return result_str
        except Exception as e:
            logger.error("Error getting random string in {}\n{}".format(__name__,e))
            return None
    
    