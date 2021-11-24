import re
from flask import make_response
from flask_cors import CORS, cross_origin


# Regular expression for validating an Email
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
 
def check_email(email):
    return re.fullmatch(email_regex, email)

@cross_origin(supports_credentials=True)
def standard_error_return(
        error_message, 
        error_code=401, 
        headers={
            'WWW.Authentication': 'Basic realm: "login required"'
        }
    ):
    return make_response(error_message, error_code, headers)