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
    def __init__(self,name,description,image_url,price,iduser,removed=False,idproduct=0):
        self.name = name
        self.image_url = image_url
        self.description = description
        self.price = price
        self.iduser = iduser
        self.removed = removed
        self.idproduct = idproduct

class Password_History:
    def __init(self,iduser,password,dateChanged):
        self.iduser=iduser
        self.password=password
        self.dateChanged=dateChanged

