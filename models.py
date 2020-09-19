from datetime import datetime

class User:
    def __init__(self,fname,lname,email,password,salt="salt",revenue=0.0,rating=0.0,passwordChangeDate=datetime.now(),incorrectLoginCount=0,userJoinDate=datetime.now(),removed=False):
        self.fname=fname
        self.lname=lname
        self.email=email
        self.password=password
        self.salt=salt
        self.revenue=revenue
        self.rating=rating
        self.passwordChangeDate=passwordChangeDate
        self.incorrectLoginCount=incorrectLoginCount
        self.userJoinDate=userJoinDate
        self.removed=removed
        self.iduser=0

class Product_listing:
    def __init__(self,name,category,price,iduser,removed=False):
        self.name = name
        self.category = category
        self.price = price
        self.iduser = iduser
        self.removed = removed

class Password_History:
    def __init(self,iduser,password,dateChanged):
        self.iduser=iduser
        self.password=password
        self.dateChanged=dateChanged

