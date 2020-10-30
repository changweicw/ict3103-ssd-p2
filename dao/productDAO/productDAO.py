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
    def __init__(self, mysql):
        self.mysql = mysql

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
    def publish_listing(self,listing):
        lastid = 0
        query_insert_product = "INSERT INTO product_listing (name,price,iduser,removed,description,stock_count) VALUES (%s,%s,%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        query_insert_image = "INSERT INTO product_images VALUES (%s,%s)"
        try:
            cur.execute(query_insert_product,(listing.name,listing.price,listing.iduser,listing.removed,listing.description,listing.stock_count))
            lastid = cur.lastrowid
            for x in listing.image_url:
                cur.execute(query_insert_image,(lastid,x))
            self.mysql.connection.commit()
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
    def retrieve_one_image(self,prod_id):
        query_select = "SELECT * FROM product_images where idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(prod_id,))
            return cur.fetchone()["imageurl"]
        except Exception as e:
            logger.error("Error retrieving single image in {}\n{}".format(__name__,e))
            return None

    # ------------------------------------------ 
    # Retrieve all products in the db
    # ------------------------------------------
    # test inputs: 
    #   -NA-
    # ------------------------------------------
    # Returns 
    #   [False]             if failed
    #   [list of products]  if success, containing
    #       [product id], [name of product],
    #       [price], [user id of owner], [product description]
    # ------------------------------------------
    def retrieve_all_products(self):
        items=[]
        query_select = "SELECT * FROM product_listing"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select)
            result = cur.fetchall()
            for x in result:
                x['price'] = float(x['price'])
            logger.info("Retrieved "+str(len(result))+" items")
            for r in result:
                r["image_url"]=self.retrieve_one_image(str(r["idproduct_listing"]))
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving all products in {}\n{}".format(__name__,e))
            return None