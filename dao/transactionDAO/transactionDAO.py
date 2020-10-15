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

logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class transactionDAO:
    def __init__(self, mysql):
        self.mysql = mysql
        self.cartDAO = cartDAO(mysql)
        self.loginDAO = loginDAO(mysql)
    
    def insert_transaction(self,idbuyer,tid):
        query_insert = "insert into transaction (idaddress,iduser_buyer,total_price,reference_id) values (%s,%s,%s,%s)"
        query_insert_billItems = "insert into bill_items (idtransaction,idproduct,product_qty,price) values (%s,%s,%s,%s)"
        try:
            address = self.loginDAO.get_address_by_id(idbuyer)
            cartItems = self.cartDAO.retrieve_cart_items(idbuyer)
            print (address)
            print (cartItems)
            totalCartPrice = sum([x['price']*x['qty'] for x in cartItems]) + 7 #calculating total price
            
            cur = self.mysql.connection.cursor()
            result_insert = cur.execute(query_insert,(address['idaddress'],idbuyer,totalCartPrice,tid))
            lastrowid = cur.lastrowid
            for x in cartItems:
                print(round(x['price']*x['qty'],2))
                cur.execute(query_insert_billItems,(lastrowid,x['idproduct'],x['qty'],round(x['price']*x['qty'],2)))
            self.mysql.connection.commit()
            return True
        except Exception as e:
            logger.error("Error in inserting into cart:"+__name__+" \n "+str(e))
            return False

    
