from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class db_helper:

    def __init__(self, mysql):
        self.mysql = mysql

    def check_login(self, email, password):
        query = "SELECT * FROM user WHERE email = %s"
        cur = self.mysql.connection.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()
        if(not result):
            return None

        if password_validator(password, result['password']):
            logger.info(email + " just logged in")
            return result
        else:
            logger.info(email + " failed to login")
            return None

    def email_exist(self, email):
        query_checkemail = "SELECT * from user where email = %s"
        cur = self.mysql.connection.cursor()
        cur.execute(query_checkemail, (email,))
        result = cur.fetchone()
        if result is not None:
            logger.info(email+" already exist")
            return True
        return False

    def signup(self, user):

        query_insert = "INSERT INTO user (fname,lname,email,password,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert + "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        try:
            enPass = encrypt_password(user.password)
            print("Password Checker: " + enPass)
            cur.execute(query_insert, (user.fname, user.lname, user.email, enPass, user.revenue,
                                       user.rating, user.passwordChangeDate, user.incorrectLoginCount, user.userJoinDate, user.removed))
            self.mysql.connection.commit()
            logger.info("Register successful for "+user.fname)

            return True
        except Exception as e:
            logger.warning(e)
            return False

    def publish_listing(self,listing):
        lastid = 0
        query_insert_product = "INSERT INTO product_listing (name,price,iduser,removed) VALUES (%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        query_insert_image = "INSERT INTO product_images VALUES (%s,%s)"
        try:
            cur.execute(query_insert_product,(listing.name,listing.price,listing.iduser,listing.removed))
            lastid = cur.lastrowid
            for x in listing.image_url:
                cur.execute(query_insert_image,(lastid,x))
            self.mysql.connection.commit()
            logger.info("Publish successful")
            return True
        except Exception as e:
            print(e)
            return False

    def retrieve_one_image(self,prod_id):
        query_select = "SELECT * FROM product_images where idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(prod_id,))
            return cur.fetchone()["imageurl"]
        except Exception as e:
            logger.error(e)

    def retrieve_all_products(self):
        items=[]
        query_select = "SELECT * FROM product_listing"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select)
            result = cur.fetchall()
            logger.info("Retrieved "+str(len(result))+" items")
            for r in result:
                r["image_url"]=self.retrieve_one_image(str(r["idproduct_listing"]))
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving products\n"+e)
