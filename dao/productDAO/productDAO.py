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

    def publish_listing(self,listing):
        lastid = 0
        query_insert_product = "INSERT INTO product_listing (name,price,iduser,removed) VALUES (%s,%s,%s,%s)"
        cur = self.mysql.connection.cursor()
        query_insert_image = "INSERT INTO product_images VALUES (%s,%s)"
        try:
            cur.execute(query_insert_product,(listing.name,listing.price,listing.iduser,listing.removed))
            lastid = cur.lastrowid
            for x in listing.image_url:
                cur.execute(query_insert_image,(lastid,x))
            self.mysql.connection.commit()
            logger.info("Publish successful")
            return True
        except Exception as e:
            print(e)
            return False

    def retrieve_one_image(self,prod_id):
        query_select = "SELECT * FROM product_images where idproduct = %s"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select,(prod_id,))
            return cur.fetchone()["imageurl"]
        except Exception as e:
            logger.error(e)

    def retrieve_all_products(self):
        items=[]
        query_select = "SELECT * FROM product_listing"
        cur = self.mysql.connection.cursor()
        try:
            cur.execute(query_select)
            result = cur.fetchall()
            logger.info("Retrieved "+str(len(result))+" items")
            for r in result:
                r["image_url"]=self.retrieve_one_image(str(r["idproduct_listing"]))
            return result
        except Exception as e:
            print(e)
            logger.error("Error retrieving products\n"+e)