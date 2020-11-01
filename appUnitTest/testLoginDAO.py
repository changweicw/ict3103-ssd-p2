from unittest import TestCase,main
from MySQLdb import connect
from appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from models import User
from unittest.mock import MagicMock,patch
import mysql.connector

class testLoginDAO(TestCase):

    @classmethod
    def setUpClass(self):
        self.db_conn = connect(
            host=DefaultConfig.MYSQL_HOST,
            user=DefaultConfig.MYSQL_USER,
            passwd=DefaultConfig.MYSQL_PASSWORD,
            db=DefaultConfig.MYSQL_DB
        )

        # self.db_conn = mysql.connector.connect(
        #     host=DefaultConfig.MYSQL_HOST,
        #     user=DefaultConfig.MYSQL_USER,
        #     password=DefaultConfig.MYSQL_PASSWORD,
        #     database=DefaultConfig.MYSQL_DB
        # )

        print("--------------------Setting up Class--------------------")
        self.loginDAO = loginDAO()

    # def test_login(self):
    #     email = "testemail@hotmail.com"
    #     password = "_Pass1234"
    #     self.assertEqual(self.loginDAO.check_login(email,password,self.db_conn).fname,email)

    @patch('dao.loginDAO.loginDAO')
    def test_update_revenue_pass(self,mockclass):
        # self.assertTrue((self.loginDAO.update_revenue(7,2,self.db_conn)))
        print(mockclass)
        assert mockclass is loginDAO


if __name__ == "__main__":
    main()