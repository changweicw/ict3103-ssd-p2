from unittest import TestCase,main
from MySQLdb import connect
from MySQLdb.cursors import DictCursor
from utils.appConfig import DefaultConfig
from dao.loginDAO.loginDAO import loginDAO
from dao.cartDAO.cartDAO import cartDAO
from dao.productDAO.productDAO import productDAO
from utils.funcs import *
from models import User,Product_listing

class testCartDAO(TestCase):
    
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
        print("[Setting up] Getting CartDAO")
        cls.cartDAO = cartDAO()
        cls.loginDAO = loginDAO()
        cls.productDAO = productDAO()

        print("[Setting up] Init class variables")
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

        print("[Setting up] Inserting 1 dummy product")
        temp_prod = Product_listing(
            "Dummy Product",
            "Best Dummy Product ever",
            ["asd.png"],
            88.88,
            cls.iduser)
        cls.idproduct = cls.productDAO.publish_listing(temp_prod,cls.db_conn)
        print("----Set up ends----")

    def test_retrieve_dashboard_products(self):
        # For logged in users, we dont want to see our products on display
        self.assertNotEqual(self.productDAO.retrieve_dashboard_products(userid = self.iduser,conn=self.db_conn),None)
        # For Non logged in users, we want to fetch all products
        self.assertNotEqual(self.productDAO.retrieve_dashboard_products(conn=self.db_conn),None)
    
    def test_publish_product(self):
        temp_prod = Product_listing(
            "prod title 1",
            "Best Product ever",
            ["asd.png"],
            20.02,
            self.iduser)
        self.assertNotEqual(self.productDAO.publish_listing(temp_prod,self.db_conn),False)

    def test_publish_product_fail_(self):
        temp_prod_neagtive_price = Product_listing(
            "prod title 1",
            "Best Product ever",
            ["https://storage.googleapis.com/3x03/2caf7520-58b8-4ae7-8737-5d2ace005407.png"],
            -20.02,
            self.iduser)

        temp_prod_broken_url = Product_listing(
            "prod title 1",
            "Best Product ever",
            ["ht\\!!)@(tps://storage.googleapis.com/3x03/2caf7520-58b8-4ae7-8737-5d2ace005407.png"],
            -20.02,
            self.iduser)

        temp_prod_invalid_name = Product_listing(
            "prod title 1<~.`",
            "Best Product!!!",
            ["https://storage.googleapis.com/3x03/2caf7520-58b8-4ae7-8737-5d2ace005407.png"],
            -20.02,
            self.iduser)

        self.assertEqual(self.productDAO.publish_listing(temp_prod_neagtive_price,self.db_conn),False)
        self.assertEqual(self.productDAO.publish_listing(temp_prod_broken_url,self.db_conn),False)
        self.assertEqual(self.productDAO.publish_listing(temp_prod_invalid_name,self.db_conn),False)

    def test_add_to_cart(self):
        self.assertEqual(self.cartDAO.add_to_cart(self.iduser,self.idproduct,1,self.db_conn),True)

    def test_add_to_cart_fail(self):
        invalid_prod_id = 6669
        invalid_user = -1
        self.assertEqual(self.cartDAO.add_to_cart(self.iduser,invalid_prod_id,1,self.db_conn),None)
        self.assertEqual(self.cartDAO.add_to_cart(invalid_user,invalid_prod_id,1,self.db_conn),None)

    @classmethod
    def tearDownClass(cls):
        print("----tear down start----")
        print("[Tearing down] Deleting dummy users".format())
        cls.loginDAO.teardown_del_addr(cls.iduser,cls.db_conn)
        cls.loginDAO.teardown_del_user(cls.email_entire_test,cls.db_conn)
        print("----tear down ends----")
    