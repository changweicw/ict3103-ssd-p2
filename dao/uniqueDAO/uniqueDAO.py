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
        query = "insert into unique_link (fk_iduser,idunique_link,category) values (%s,%s,%s)"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (iduser,unique,category))
            self.mysql.connection.commit()
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while inserting unique link in "+__name__+":" +str(e))
    
    def delete_unik_by_iduser(self,iduser):
        query = "delete from unique_link where fk_iduser = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (iduser,))
            self.mysql.connection.commit()
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while deleting unque link by user id in "+__name__+":" +str(e))
            

    def delete_unik_by_string(self,string):
        query = "delete from unique_link where idunique_link = %s"
        try:
            cur = self.mysql.connection.cursor()
            cur.execute(query, (string,))
            self.mysql.connection.commit()
        except Exception as e:
            logger.error("unique string: "+string+" encountered an error while deleting unique link by string in "+__name__+":" +str(e))
            