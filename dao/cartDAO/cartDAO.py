from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
from dao.productDAO.productDAO import productDAO
import models

logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class cartDAO:
    def __init__(self, mysql):
        self.mysql = mysql
        self.productDAO = productDAO(mysql)

    # ------------------------------------------ 
    # Get a single item from the cart.
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to retrieve]
    # ------------------------------------------
    # Return OBJECT containing:
    #   [product id], [name], [price], [id of product owner],
    #   [removed], [stock_count], [description], 
    #   [id of user that posess the item in the cart]
    # ------------------------------------------
    def get_cart_single(self,iduser,idproduct):
        query_select = "select * from product_listing p inner join cart c \
        ON p.idproduct_listing = c.idproduct where c.iduser =  %s and c.idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(iduser,idproduct))
            result = cur.fetchone()
            logger.info("User "+str(iduser)+" attempted to retrieve a cart item")
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving cart\n"+str(e))

    # ------------------------------------------ 
    # Retrieve all cart item information
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to retrieve]
    #   #2 - [invalid user id]
    # ------------------------------------------
    # Returns is a LIST of OBJECTS containing:
    #   [product id], [name], [price], [id of product owner],
    #   [removed], [stock_count], [description], 
    #   [id of user that posess the item in the cart]
    # ------------------------------------------
    
    def retrieve_cart_items(self,iduser):
        query_select = "select * from product_listing p inner join cart c ON p.idproduct_listing = c.idproduct where c.iduser =  %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(iduser,))
            result = cur.fetchall()
            for x in result:
                x['price'] = float(x['price'])
                x["image_url"]=self.productDAO.retrieve_one_image(str(x["idproduct_listing"]))
            # for r in result:
            #     r["image_url"]=self.productDAO.retrieve_one_image(str(r["idproduct_listing"]))
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving cart\n"+str(e))

    # ------------------------------------------ 
    # Add item to cart
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to retrieve], [id of product to be added], [1]
    #   #2 - [id of user we want to retrieve], [id of product to be added], [0]
    #   #3 - [id of user we want to retrieve], [id of product to be added], [-1]
    #   #4 - [invalid user id], [id of product to be added], [1]
    # ------------------------------------------
    # Return:
    #   [None] if failed
    #   [not None] if success
    # ------------------------------------------
    def add_to_cart(self,iduser,idproduct,qty):
        query_insert = "insert into cart (iduser,idproduct,qty) values(%s,%s,%s)"
        singleItem = self.get_cart_single(iduser,idproduct)
        if singleItem:
            return self.update_cart_qty(iduser,idproduct,singleItem['qty']+qty)
        
        cur = self.mysql.connection.cursor()
        try:
            result = cur.execute(query_insert,(iduser,idproduct,qty))
            self.mysql.connection.commit()
            return result
        except Exception as e:
            logger.error("Error in add to cart:"+__name__+" \n "+str(e))
            return None

    # ------------------------------------------ 
    # Updating item qty in cart
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to update], [id of product to be added], [1]
    #   #2 - [id of user we want to update], [id of product to be added], [0]
    #   #3 - [id of user we want to update], [id of product to be added], [-1]
    # ------------------------------------------
    # Return:
    #   [None] if failed
    #   [not None] if success
    # ------------------------------------------
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

    # ------------------------------------------ 
    # Deleting item in cart
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to delete], [id of product to be added]
    # ------------------------------------------
    # Return:
    #   [None] if failed
    #   [not None] if success
    # ------------------------------------------
    def delete_from_cart(self,iduser,idproduct):
        query = "delete from cart where iduser = %s and idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            result = cur.execute(query,(iduser,idproduct))
            self.mysql.connection.commit()
            return result
        except Exception as e:
            logger.error("Error in deleting from cart:"+__name__+" \n "+str(e))
            return None

    # ------------------------------------------ 
    # Deleting entire cart items
    # ------------------------------------------
    # test inputs: 
    #   #1 - [id of user we want to delete]
    # ------------------------------------------
    # Return:
    #   [None] if failed
    #   [not None] if success
    # ------------------------------------------
    def empty_cart(self,iduser):
        query = "delete from cart where iduser = %s"
        cur = self.mysql.connection.cursor()
        try:
            result=cur.execute(query,(iduser,))
            self.mysql.connection.commit()
            return result
        except Exception as e:
            logger.error("Error in deleting entire cart:"+__name__+" \n "+str(e))
            return None

    