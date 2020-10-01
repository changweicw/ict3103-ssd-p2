from datetime import datetime
from models import User,Product_listing
import logging
from flask_mysqldb import MySQL
from google.cloud import storage
from log_helper import *
from flask import Flask,current_app


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class uniqueDAO:
    def __init__(self,mysql):
        self.mysql = mysql
    
    def search_unik(self,unik):
        query="Select * from unique_link where idunique_link = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (unik,))
            result = cur.fetchone()
            return result or None
        except Exception as e:
            logger.error("encountered an error while retrieving unqik link in "+__name__+":" +str(e))
            return None

    def insert_unik(self,iduser,unique,category):
        query = "insert into unqiue_link (fk_iduser,idunique_link,category) values (%s,%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (iduser,unique,category))
            self.mysql.connection.commit()
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while inserting unik link in "+__name__+":" +str(e))