from unittest import TestCase,main
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from models import User
from unittest.mock import MagicMock,patch
import mysql.connector

class testLoginDAO(TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("[Setting up] Creating db connection")
        cls.db_conn = connect(
            host=DefaultConfig.MYSQL_HOST,
            user=DefaultConfig.MYSQL_USER,
            passwd=DefaultConfig.MYSQL_PASSWORD,
            db=DefaultConfig.MYSQL_DB,
            cursorclass=DictCursor
        )
        print("[Setting up] Getting loginDAO")
        cls.loginDAO = loginDAO()

        print("[Setting up] Init class variables")
        cls.email_register = "unittesting@hotmail.com"
        cls.email = "testemail@hotmail.com"
        cls.password = "_Pass1234"
        cls.fname = "Unittesting"
        cls.lname = "Tan"
        cls.revenue_to_update = 3

    def test_register(self):
        user = User(self.fname, self.lname, self.email_register, self.password)
        self.assertEqual(self.loginDAO.signup(user,self.db_conn),True)

    def test_login(self):
        tempuser=self.loginDAO.check_login(self.email,self.password,self.db_conn)
        self.assertEqual(tempuser.email,self.email)

    def test_read_user(self):
        self.assertEqual(self.loginDAO.get_user_by_email(self.email,self.db_conn).email,self.email)

    def test_update_revenue(self):
        tempUser = self.loginDAO.get_user_by_email(self.email,self.db_conn)
        self.assertEqual(self.loginDAO.update_revenue(tempUser.iduser,self.revenue_to_update,self.db_conn),True)

    @classmethod
    def tearDownClass(cls):
        print("[Tearing down] Deleting user {}".format(cls.email_register))
        cls.loginDAO.teardown_del_user(cls.email_register,cls.db_conn)


if __name__ == "__main__":
    main()