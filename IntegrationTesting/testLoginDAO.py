from unittest import TestCase,main
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from utils.appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from utils.funcs import *
from models import User
from unittest.mock import MagicMock,patch

class testLoginDAO(TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("----Set up start----")
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
        cls.email_entire_test = "utuser@hotmail.com"
        cls.password = "_Pass1234"
        cls.fname = "Unittesting"
        cls.lname = "Tan"
        cls.revenue_to_update = 3
        cls.iduser = None

        print("[Setting up] Creating a dummy user")
        user = User(cls.fname, cls.lname, cls.email_entire_test, cls.password)
        cls.loginDAO.signup(user,cls.db_conn)
        cls.iduser = cls.loginDAO.get_user_by_email(cls.email_entire_test,cls.db_conn).iduser

        print("----Set up ends----")

    def test_register(self):
        # email_register = "unittesting@hotmail.com"
        # password = "_Pass1234"
        # fname = "Unittesting"
        # lname = "Tan"
        user = User(self.fname, self.lname, self.email_register, self.password)
        self.assertEqual(self.loginDAO.signup(user,self.db_conn),True)

    def test_register_fail_common_password(self):
        # email_register = "unittesting@hotmail.com"
        # password = "common"
        # fname = "Unittesting"
        # lname = "Tan"
        user = User(self.fname, self.lname, "unique"+self.email_register, "common")
        self.assertEqual(self.loginDAO.signup(user,self.db_conn),None)

    def test_login(self):
        # email_entire_test = "utuser@hotmail.com"
        # password = "_Pass1234"
        tempuser=self.loginDAO.check_login(self.email_entire_test,self.password,self.db_conn)
        self.assertEqual(tempuser.email,self.email_entire_test)

    def test_login_fail_wrong_credentials(self):
        # email_register = "unittesting@hotmail.com"
        # email_entire_test = "utuser@hotmail.comhey"
        # password = "_Pass1234"
        tempuser=self.loginDAO.check_login(self.email_entire_test+"hey",self.password,self.db_conn)
        self.assertEqual(tempuser,None)

    def test_update_addr(self):
        line = "The building Street 61"
        unitno = "#04-14"
        zipcode = "123456"
        addrObj = {"line":line,"unitno":unitno,"zipcode":zipcode}
        self.assertEqual(self.loginDAO.update_address(self.iduser,addrObj,self.db_conn),True)

    def test_update_addr_fail_special_char(self):
        line = "The building Street 61!!!`"
        unitno = "#04-14"
        zipcode = "123456"
        addrObj = {"line":line,"unitno":unitno,"zipcode":zipcode}
        self.assertEqual(self.loginDAO.update_address(self.iduser,addrObj,self.db_conn),None)


    @classmethod
    def tearDownClass(cls):
        print("----tear down start----")
        print("[Tearing down] Deleting dummy users".format())
        cls.loginDAO.teardown_del_addr(cls.iduser,cls.db_conn)
        cls.loginDAO.teardown_del_user(cls.email_register,cls.db_conn)
        cls.loginDAO.teardown_del_user(cls.email_entire_test,cls.db_conn)
        print("----tear down ends----")


if __name__ == "__main__":
    main()