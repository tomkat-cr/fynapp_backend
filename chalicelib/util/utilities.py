import datetime
import re
import sys
import traceback

from flask import jsonify, make_response
from flask_cors import cross_origin

from chalicelib.util.app_logger import log_warning, log_debug


# Email validation regular expression
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


# Check that an email address is valid
def check_email(email):
    return re.fullmatch(email_regex, email)


# Getting the current UTC date and time as a timestamp
def current_datetime_timestamp():
    dt = datetime.datetime.now(datetime.timezone.utc)
    utc_time = dt.replace(tzinfo=datetime.timezone.utc)
    utc_timestamp = utc_time.timestamp()
    return utc_timestamp


# Returns an statdard base resultset, to be used in the building
# of responses to the outside world
def get_default_resultset():
    resultset = {
        'error': False,
        'error_message': None,
        'resultset': {}
    }
    return resultset


# Standard way to return results to to outside world.
# If there's an error, returns a header with an HTTP error code
def return_resultset_jsonified_or_exception(
    result, http_error=400
):  # Error HTTP 400 = Bad request
    # log_debug(
    #   'return_resultset_jsonified_or_exception |' +
    #   ' result: {} | http_error: {}'.format(result, http_error)
    # )
    if result['error'] or result['error_message']:
        log_debug(
            'return_resultset_jsonified_or_exception |' +
            ' ERROR error_message: {} | http_error: {}'.format(
                result['error_message'], http_error
            )
        )
        return standard_error_return(result['error_message'], http_error)
    # log_debug(
    #   'return_resultset_jsonified_or_exception |' +
    #   ' jsonify(result): {}'.format(jsonify(result))
    # )
    # log_debug(
    #   'return_resultset_jsonified_or_exception |' +
    #   ' jsonify(result[\'resultset\']): {}'.format(
    #       jsonify(result['resultset'])
    #   )
    # )
    response = jsonify(result)
    # response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# When a BaseException is fired, use this method to return
# a standard error message
def get_standard_base_exception_msg(err, message_code='NO_E_CODE'):
    message_code = f"[{message_code=}]" if message_code == '' else ''
    response = f"Unexpected {err=}, {type(err)=} {message_code=}"
    log_warning(response)
    log_warning(format_stacktrace())
    return response


def format_stacktrace():
    parts = ["Traceback (most recent call last):\n"]
    parts.extend(traceback.format_stack(limit=25)[:-2])
    parts.extend(traceback.format_exception(*sys.exc_info())[1:])
    return "".join(parts)


# Standard error returns
@cross_origin(supports_credentials=True)
def standard_error_return(
    error_message,
    error_code=401,  # Unauthorized
    headers={
        'WWW.Authentication': 'Basic realm: "login required"'
    }
):
    return make_response(error_message, error_code, headers)
