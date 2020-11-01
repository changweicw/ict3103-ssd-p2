from models import User,Product_listing
import logging
from bcrypt_hashing import encrypt_password, password_validator
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app
from flask_mysqldb import MySQL

logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class productDAO:
    

    # ------------------------------------------ 
    # Insert new item
    # ------------------------------------------
    # test inputs: 
    #   #1 - [object containing product information including image url]
    #   #2 - [invalid object]
    # ------------------------------------------
    # Returns 
    #   [False]                 if failed
    #   [new product id (int)]  if success
    # ------------------------------------------
    def publish_listing(self,listing,conn=None):
        lastid = 0
        query_insert_product = "INSERT INTO product_listing (name,price,iduser,removed,description,stock_count) VALUES (%s,%s,%s,%s,%s,%s)"
        cur = conn.cursor()
        query_insert_image = "INSERT INTO product_images VALUES (%s,%s)"
        try:
            cur.execute(query_insert_product,(listing.name,listing.price,listing.iduser,listing.removed,listing.description,listing.stock_count))
            lastid = cur.lastrowid
            for x in listing.image_url:
                cur.execute(query_insert_image,(lastid,x))
            conn.commit()
            logger.info("Publish successful")
            return lastid
        except Exception as e:
            logger.error("Error inserting product into db in {}\n{}".format(__name__,e))
            return False

    # ------------------------------------------ 
    # Retrieve first image's url of product
    # ------------------------------------------
    # test inputs: 
    #   #1 - [product id]
    #   #2 - [invalid product id]
    # ------------------------------------------
    # Returns 
    #   [False]                 if failed
    #   [image url (string)]    if success
    # ------------------------------------------
    def retrieve_one_image(self,prod_id,conn=None):
        query_select = "SELECT * FROM product_images where idproduct = %s"
        cur = conn.cursor()
        try:
            cur.execute(query_select,(prod_id,))
            return cur.fetchone()["imageurl"]
        except Exception as e:
            logger.error("Error retrieving single image in {}\n{}".format(__name__,e))
            return None

    # ------------------------------------------ 
    # Retrieve all products in the db not including the one calling
    # ------------------------------------------
    # test inputs: 
    #   #1 - [valid id]
    #   #2 - empty user id
    # ------------------------------------------
    # Returns 
    #   [False]             if failed
    #   [list of products]  if success, containing
    #       [product id], [name of product],
    #       [price], [user id of owner], [product description]
    # ------------------------------------------
    def retrieve_all_products(self, userid=-1,conn=None):
        items=[]
        query_select = "SELECT * FROM product_listing where iduser not like %s"
        cur = conn.cursor()
        try:
            cur.execute(query_select,(userid,))
            result = cur.fetchall()
            for x in result:
                x['price'] = float(x['price'])
                x["image_url"]=self.retrieve_one_image(str(x["idproduct_listing"]),conn)
            return result
        except Exception as e:
            logger.error("Error retrieving all products in {}\n{}".format(__name__,e))
            return None

    # ------------------------------------------ 
    # Retrieve all products in the db of the one calling
    # ------------------------------------------
    # test inputs: 
    #   #1 - [valid id]
    # ------------------------------------------
    # Returns 
    #   [False]             if failed
    #   [list of products]  if success, containing
    #       [product id], [name of product],
    #       [price], [user id of owner], [product description]
    # ------------------------------------------
    def retrieve_dashboard_products(self,userid,conn=None):
        items=[]
        query_select = "SELECT * FROM product_listing where iduser not like %s"
        cur = conn.cursor()
        try:
            cur.execute(query_select,(userid,))
            result = cur.fetchall()
            for x in result:
                x['price'] = float(x['price'])
                x["image_url"]=self.retrieve_one_image(str(x["idproduct_listing"]),conn)
            return result
        except Exception as e:
            logger.error("Error retrieving all products in {}\n{}".format(__name__,e))
            return None

    # ------------------------------------------ 
    # Retrieve one product in the db
    # ------------------------------------------
    # test inputs: 
    #   #1 - [valid id]
    #   #2 - empty user id
    # ------------------------------------------
    # Returns 
    #   [False]             if failed
    #   [list of products]  if success, containing
    #       [product id], [name of product],
    #       [price], [user id of owner], [product description]
    # ------------------------------------------
    def retrieve_one_product(self, id,conn=None):
        query_select = "SELECT * FROM product_listing where idproduct_listing = %s"
        cur = conn.cursor()
        try:
            cur.execute(query_select,(id,))
            result = cur.fetchone()
            result['price'] = float(result['price'])
            result["image_url"]=self.retrieve_one_image(str(result["idproduct_listing"]),conn)
            return result
        except Exception as e:
            logger.error("Error retrieving all products in {}\n{}".format(__name__,e))
            return None