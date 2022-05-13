# Function to set a cookie header (Takes age and options** as additional parameters)
def set_cookie(given_cookie: str, age=3600, options=''):
    cookie = "\r\nSet-Cookie: "
    cookie += given_cookie
    cookie += '; Max-Age=' + str(age)
    cookie += options
    return cookie
