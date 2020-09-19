import bcrypt as bcrypt


def encrypt_password(entered_password):

    encoded_enc_pw = entered_password.encode("utf-8")
    encrypted_pw = bcrypt.hashpw(encoded_enc_pw, bcrypt.gensalt())
    return encrypted_pw.decode("utf-8")


def password_validator(entered_password, hashed_password):

    encoded_plaintext = entered_password.encode("utf-8")
    encoded_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(encoded_plaintext, encoded_password)
