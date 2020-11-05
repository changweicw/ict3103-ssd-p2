from unittest import TestCase,main
from utils.funcs import *
from utils.mailing import *
from utils.bcrypt_hashing import *

class testFuncs(TestCase):
    
    def test_password_validator(self):
        pw = "_Pass1234"
        self.assertEqual(check_password(pw),True)

    def test_password_validator_Fail(self):
        pw = "_P1111"
        pw_1 = "12345678"
        pw_2 = "abcd1234"
        self.assertEqual(check_password(pw),False)
        self.assertEqual(check_password(pw_1),False)
        self.assertEqual(check_password(pw_2),False)

    def test_Email_validator(self):
        email = "realEmail@mail.com"
        self.assertEqual(check_email(email),True)

    def test_Email_validator_Fail(self):
        email = "@#!$!$ @mail.com"
        email_1 = "Tommy@!231*&^.com"
        email_2 = "Tommy@mail. 123"
        self.assertEqual(check_email(email),False)
        self.assertEqual(check_email(email_1),False)
        self.assertEqual(check_email(email_2),False)

    def test_Name_validator(self):
        name = "Tommy"
        name_1 = "Tommy Lim Chu Choo"
        self.assertEqual(check_name(name),True)
        self.assertEqual(check_name(name_1),True)

    def test_Name_validator_Fail(self):
        name = "Tommy@@"
        name_1 = "! Tmmy"
        self.assertEqual(check_name(name),False)
        self.assertEqual(check_name(name_1),False)
    
    def test_Address_validator(self):
        addr = "Blk 651 Upper Serangoon #04-14"
        self.assertEqual(check_addr(addr),True)

    def test_Address_validator_Fail(self):
        addr = "Blk 651 Upper Serangoon #04-14!!*&"
        self.assertEqual(check_addr(addr),False)

    def test_bcrypt_encrypt_decrypt(self):
        pw = "_Pass1234"
        entered_pw = "_Pass1234"
        pw_encrypted = encrypt_password(pw)
        self.assertEqual(password_validator(entered_pw,pw_encrypted),True)

    def test_bcrypt_encrypt_decrypt_Fail(self):
        pw = "_Pass1234"
        entered_pw = "_Fail1234"
        pw_encrypted = encrypt_password(pw)
        self.assertEqual(password_validator(entered_pw,pw_encrypted),False)

    
