from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
from flask_mysqldb import MySQL
from dao.cartDAO.cartDAO import cartDAO
from dao.loginDAO.loginDAO import loginDAO
from dao.productDAO.productDAO import productDAO

logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class transactionDAO:
    def __init__(self):
        self.cartDAO = cartDAO()
        self.loginDAO = loginDAO()
        self.productDAO = productDAO()
    
    # ------------------------------------------ 
    # inserts a transaction consisting of payment details
    # minimal product details
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of buyer], [transaction id]
    # ------------------------------------------
    # Returns 
    #   [True]  if success
    #   [None]  if failed
    # ------------------------------------------
    def insert_transaction(self,idbuyer,tid,conn=None):
        query_insert = "insert into transaction (idaddress,iduser_buyer,total_price,reference_id) values (%s,%s,%s,%s)"
        query_insert_billItems = "insert into bill_items (idtransaction,idproduct,product_qty,price) values (%s,%s,%s,%s)"
        try:
            address = self.loginDAO.get_address_by_id(idbuyer,conn)
            cartItems = self.cartDAO.retrieve_cart_items(idbuyer,conn)
            totalCartPrice = sum([x['price']*x['qty'] for x in cartItems]) + 7 #calculating total price
            for item in cartItems:
                self.loginDAO.update_revenue(item['iduser'],item['price']*item['qty'],conn)

            cur = conn.cursor()
            result_insert = cur.execute(query_insert,(address['idaddress'],idbuyer,totalCartPrice,tid))
            lastrowid = cur.lastrowid

            for x in cartItems:
                cur.execute(query_insert_billItems,(lastrowid,x['idproduct'],x['qty'],round(x['price']*x['qty'],2)))
            conn.commit()

            return True
        except Exception as e:
            logger.error("Error in inserting into transaction:"+__name__+" \n "+str(e))
            return None

    # ------------------------------------------ 
    # gets total price of that transaction
    # ------------------------------------------
    # test inputs: 
    #   #1 - [transaction id]
    # ------------------------------------------
    # Returns 
    #   [decimal price]  if success
    #   [None]  if failed
    # ------------------------------------------
    def read_transaction_total_price(self,tid,conn=None):
        query_select = "select sum(product_qty*price) as total from bill_items where idtransaction = %s"
        cur = conn.cursor()
        try:
            cur.execute(query_select,(tid,))
            result = cur.fetchone()
            return result["total"]
        except Exception as e:
            logger.error("Error retrieving all products in {}\n{}".format(__name__,e))
            return None
