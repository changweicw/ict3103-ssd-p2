from datetime import datetime
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,fname,lname,email,password,total_revenue=0.0,rating=0.0,passwordChangeDate=datetime.now(),incorrectLoginCount=0,userJoinDate=datetime.now(),removed=False,iduser=-1,addr={}):
        self.fname=fname
        self.lname=lname
        self.email=email
        self.password=password
        self.total_revenue=total_revenue
        self.rating=rating
        self.passwordChangeDate=passwordChangeDate
        self.incorrectLoginCount=incorrectLoginCount
        self.userJoinDate=userJoinDate
        self.removed=removed
        self.iduser=iduser
        self.address_details = addr

    def get_id(self):
        return self.iduser


class Product_listing:
    def __init__(self,name,description,image_url,price,iduser,removed=False,idproduct=0,stock_count=100):
        self.name = name
        self.image_url = image_url
        self.description = description
        self.price = price
        self.iduser = iduser
        self.removed = removed
        self.idproduct = idproduct
        self.stock_count = stock_count

class Password_History:
    def __init(self,iduser,password,dateChanged):
        self.iduser=iduser
        self.password=password
        self.dateChanged=dateChanged

