from datetime import datetime
from models import User,Product_listing
import logging
from flask_mysqldb import MySQL
from google.cloud import storage
from utils.log_helper import *
from flask import Flask,current_app


logger = prepareLogger(__name__,'db.log',logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

class uniqueDAO:
  
    
    # ------------------------------------------ 
    # Checking if unique link is valid
    # ------------------------------------------
    # test inputs: 
    #   #1 - [valid unqiue link]
    # ------------------------------------------
    # Returns 
    #   [no None]  if success
    #   [None]  if failed
    # ------------------------------------------
    def search_unik(self,unik,conn=None):
        query="Select * from unique_link where idunique_link = %s"
        try:
            cur = conn.cursor()
            cur.execute(query, (unik,))
            result = cur.fetchone()
            return result or None
        except Exception as e:
            logger.error("encountered an error while retrieving unqik link in "+__name__+":" +str(e))
            return None

    # ------------------------------------------ 
    # Inserting a unique link
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id the link belongs to], [valid unqiue link],
    #           [category of the link, password etc]
    # ------------------------------------------
    # Returns 
    #   [no None]  if success
    #   [None]  if failed
    # ------------------------------------------
    def insert_unik(self,iduser,unique,category,conn=None):
        query = "insert into unique_link (fk_iduser,idunique_link,category) values (%s,%s,%s)"
        try:
            cur = conn.cursor()
            result = cur.execute(query, (iduser,unique,category))
            conn.commit()
            return result
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while inserting unique link in "+__name__+":" +str(e))
            return None
    
    # ------------------------------------------ 
    # Deleting a unique link using user id
    # ------------------------------------------
    # test inputs: 
    #   #1 - [user id the link belongs to]
    # ------------------------------------------
    # Returns 
    #   [no None]  if success
    #   [None]  if failed
    # ------------------------------------------
    def delete_unik_by_iduser(self,iduser,conn=None):
        query = "delete from unique_link where fk_iduser = %s"
        try:
            cur = conn.cursor()
            result=cur.execute(query, (iduser,))
            conn.commit()
            return result
        except Exception as e:
            logger.error("User "+str(iduser)+ " encountered an error while deleting unque link by user id in "+__name__+":" +str(e))
            return None
            
    # ------------------------------------------ 
    # Deleting a unique link using the key itself
    # ------------------------------------------
    # test inputs: 
    #   #1 - [string of the link to be deleted]
    # ------------------------------------------
    # Returns 
    #   [no None]  if success
    #   [None]  if failed
    # ------------------------------------------
    def delete_unik_by_string(self,string,conn=None):
        query = "delete from unique_link where idunique_link = %s"
        try:
            cur = conn.cursor()
            result=cur.execute(query, (string,))
            self.mysql.connection.commit()
            return result
        except Exception as e:
            logger.error("unique string: "+string+" encountered an error while deleting unique link by string in "+__name__+":" +str(e))
            return None
            