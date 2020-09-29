from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
import models

logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class cartDAO:
    def __init__(self, mysql):
        self.mysql = mysql

    def get_cart_single(self,iduser,idproduct):
        query_select = "select * from product_listing p inner join cart c ON p.idproduct_listing = c.idproduct where c.iduser =  %s and c.idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(iduser,idproduct))
            result = cur.fetchone()
            logger.info("User "+str(iduser)+" attempted to retrieve a cart item")
            print(result)
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving cart\n"+str(e))

    def get_cart_items(self,iduser):
        query_select = "select * from product_listing p inner join cart c ON p.idproduct_listing = c.idproduct where c.iduser =  %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(iduser,))
            result = cur.fetchall()
            logger.info("User "+str(iduser)+" Retrieved "+str(len(result))+" cart items")
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving cart\n"+str(e))

    def add_to_cart(self,iduser,idproduct,qty):
        query_insert = "insert into cart (iduser,idproduct,qty) values(%s,%s,%s)"
        singleItem = self.get_cart_single(iduser,idproduct)
        if singleItem:
            print("why")
            return self.update_cart_qty(iduser,idproduct,singleItem['qty']+qty)
        
        cur = self.mysql.connection.cursor()
        try:
            result = cur.execute(query_insert,(iduser,idproduct,qty))
            self.mysql.connection.commit()
            return result
        except Exception as e:
            logger.error("Error in add to cart:"+__name__+" \n "+str(e))
            return None

    def update_cart_qty(self,iduser,idproduct,qty):
        query_update = "update cart set qty = %s where iduser = %s and idproduct = %s"
        cur = self.mysql.connection.cursor()
        if qty<=0:
            return self.delete_from_cart(iduser,idproduct)
        try:
            affected_rows = cur.execute(query_update,(qty,iduser,idproduct))
            self.mysql.connection.commit()
            return affected_rows
        except Exception as e:
            logger.error("Error in increase cart qty:"+__name__+" \n "+str(e))
            return None

    def delete_from_cart(self,iduser,idproduct):
        query = "delete from cart where iduser = %s and idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query,(iduser,idproduct))
            self.mysql.connection.commit()
        except Exception as e:
            logger.error("Error in deleting from cart:"+__name__+" \n "+str(e))