from models import User
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL

logger = logging.getLogger(__name__)
fh = logging.FileHandler('db.log')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)
logger.setLevel(logging.INFO)


class db_helper:

    def __init__(self, mysql):
        self.mysql = mysql

    def check_login(self, email, password):
        query = "SELECT * FROM users WHERE email = %s"
        cur = self.mysql.connection.cursor()
        cur.execute(query, (email,))
        result = cur.fetchone()

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

        query_insert = "INSERT INTO users (fname,lname,email,password,password_salt,total_revenue,rating_avg,password_change_date,incorrect_login_count,user_join_date,removed) "
        query_insert = query_insert + \
            "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        try:
            enPass = encrypt_password(user.password)
            print("Password Checker: " + enPass)
            cur.execute(query_insert, (user.fname, user.lname, user.email, enPass, user.salt, user.revenue,
                                       user.rating, user.passwordChangeDate, user.incorrectLoginCount, user.userJoinDate, user.removed))
            self.mysql.connection.commit()
            logger.info("Register successful for "+user.fname)

            return True
        except Exception as e:
            logger.warning("Register failed\n"+e)
            return False
