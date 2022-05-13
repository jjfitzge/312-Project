import bcrypt
import random
import string

# Function to get the salt and saltedhash for an inputted password/authentication token


def get_saltedhash(password):
    enc_pass = password.encode()
    salt = bcrypt.gensalt()
    saltedhash = bcrypt.hashpw(enc_pass, salt)
    return {"salt": salt, "saltedhash": saltedhash}

# Function to generate an authentication token upon signing in succesfully


def gen_authToken():
    length = 50
    token = ''.join(random.choice(string.ascii_letters + string.digits)
                    for _ in range(length))
    print("---------------------------------------")
    print("Generated Auth Token: ", token)
    print("---------------------------------------")
    return token

# Function that produces a saltedhash given a password and salt for comparing User password's AND Authentication tokens


def check_salt(password, salt):
    enc_pass = password.encode()
    saltedhash = bcrypt.hashpw(enc_pass, salt)
    return saltedhash
