from models import User,Product_listing
import logging
from flask_mysqldb import MySQL
from google.cloud import storage


logger = logging.getLogger(__name__)
fh = logging.FileHandler('db.log')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)
logger.setLevel(logging.INFO)

class db_helper:
    
    def __init__(self,mysql):
        self.mysql=mysql

    def check_login(self,email, password):
        query = "SELECT * FROM user WHERE email = %s AND password = %s"
        cur = self.mysql.connection.cursor()
        cur.execute(query, (email,password))
        result = cur.fetchone()
        if result:
            logger.info(email+" just logged in")
            return result
        else:
            logger.info(email+" failed to login")
            return None
            

    def email_exist(self,email):
        query_checkemail="SELECT * from user where email = %s"
        cur = self.mysql.connection.cursor()
        cur.execute(query_checkemail,(email,))
        result = cur.fetchone()
        if result is not None:
            logger.info(email+" already exist")
            return True
        return False

    def signup(self,user):
        

        query_insert = "INSERT INTO user (fname,lname,email,password,password_salt,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert+ "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        try:
            
            cur.execute(query_insert,(user.fname,user.lname,user.email,user.password,user.salt,user.revenue,user.rating,user.passwordChangeDate,user.incorrectLoginCount,user.userJoinDate,user.removed))
            self.mysql.connection.commit() 
            logger.info("Register successful for "+user.fname)
            
            return True
        except Exception as e:
            logger.warning("Register failed\n"+e)
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
