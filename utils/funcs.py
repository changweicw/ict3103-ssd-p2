import re
from utils.appConfig import DefaultConfig


# ------------------------------------------ 
# Using regex to check name requireent
# ------------------------------------------
# test inputs: 
#   #1 - [proper name of 2 char, words and spaces only]
#   #2 - [Improper name of 1 char]
#   #3 - [Improper name of 3 char with symbols]
# ------------------------------------------
# Return:
#   [False] if failed
#   [True] if matched
# ------------------------------------------
def check_name(name):
    nameRegex = "(^[\w\s]{1,}[\w\s]{1,}$)"
    pat = re.compile(nameRegex)
    return True if re.search(pat,name) else False

# ------------------------------------------ 
# Using regex to check password requireent
# ------------------------------------------
# test inputs: 
#   #1 - [proper password of 8 characters ]
#   #2 - [Improper name of 1 char]
#   #3 - [Improper name of 3 char with symbols]
# ------------------------------------------
# Return:
#   [False] if failed
#   [True] if matched
# ------------------------------------------
def check_password(password):
    passwordRegex = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-_]).{8,}$"
    pat = re.compile(passwordRegex)
    return True if re.search(pat,password) else False

# ------------------------------------------ 
# Using regex to check email requireent
# ------------------------------------------
# test inputs: 
#   #1 - [>=1 character , @ , >=1 char, \. , >=2char]
#   #2 - [anyting else]
# ------------------------------------------
# Return:
#   [False] if failed
#   [True] if matched
# ------------------------------------------
def check_email(email):
    emailRegex = "^(([^<>()\[\]\\.,;:\s@\"]+(\.[^<>()\[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$"
    pat = re.compile(emailRegex)
    return True if re.search(pat,email) else False

# ------------------------------------------ 
# Using regex to check address requireent
# ------------------------------------------
# test inputs: 
#   #1 - [a-z upper/lower, numbers, dash, pound sign, min1 max65]
#   #2 - [anyting else]
# ------------------------------------------
# Return:
#   [False] if failed
#   [True] if matched
# ------------------------------------------
def check_addr(addr):
    addRegex = "^([a-zA-Z0-9-# ]{1,65})$"
    pat = re.compile(addRegex)
    return True if re.search(pat,addr) else False

# ------------------------------------------ 
# Using regex to check zipcode requireent
# ------------------------------------------
# test inputs: 
#   #1 - [numbers exactly 6 char long]
#   #2 - [anyting else]
# ------------------------------------------
# Return:
#   [False] if failed
#   [True] if matched
# ------------------------------------------
def check_zipcode(zipC):
    zipRegex = "[0-9]{6,6}"
    pat = re.compile(zipRegex)
    return True if re.search(pat,zipC) else False

# ------------------------------------------ 
# Checking if it is common password
# ------------------------------------------
# test inputs: 
#   #1 - [numbers exactly 6 char long]
#   #2 - [anyting else]
# ------------------------------------------
# Return:
#   [None] if failed
#   [not None] if matched
# ------------------------------------------
def isCommonPassword(password):
    f = open(DefaultConfig.PASSWORD_COMMON_FILENAME, "r")
    for x in f:
        if password in x:
            return True
    return False