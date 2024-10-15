import os
import re
import jwt
import base64
import json
import logging
import sys


## Env vars for most auth methods:
TYK_LOGIN_TARGET_URL = os.getenv("TYK_LOGIN_TARGET_URL")
SERVICE_NAME = os.getenv("SERVICE_NAME")
CANDIG_USER_KEY = os.getenv("CANDIG_USER_KEY", "email")
DEBUG_MODE = os.getenv("DEBUG_MODE")


## Format for logging:
# we don't include the container and the timestamp here
# because the fluentd plugin will add those
LOG_FORMAT = 'level: %(levelname)s, file: %(name)s, log: %(message)s'


class CandigLoggingError(Exception):
    pass


def get_auth_token(request=None):
    """
    Extracts token from request's Authorization header
    """
    try:
        token = request.headers['Authorization']
        if token is None:
            return None
        return token.split()[1]
    except:
        return None


def get_session_details(request=None):
    result = {}
    token = get_auth_token(request)
    if token is not None:
        decoded = jwt.decode(token, options={"verify_signature": False})
        result = {"user": decoded[CANDIG_USER_KEY], "sid": decoded['sid']}
    return result


def initialize():
    if DEBUG_MODE == "1":
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, stream=sys.stdout)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, stream=sys.stdout)



class CanDIGLogger:
    def __init__(self, file_name):
        self.logger = logging.getLogger(file_name)


    def compile_message(self, message, request):
        result = {"message": message}
        if request is not None:
            if hasattr(request, "path"):
                result["path"] = request.path
            elif hasattr(request, "url"): # this is what it's called in Requests.request
                result["path"] = request.url
            if hasattr(request, "method"):
                result["method"] = request.method
            ## query parameters
            if hasattr(request, "query_string"): # this is what it's called in a Flask request
                result["query"] = request.args.to_dict()
            elif hasattr(request, "GET"): # this is what it's called in a Django HttpRequest
                result["query"] = request.GET.dict()
            elif hasattr(request, "POST"): # this is what it's called in a Django HttpRequest
                result["query"] = request.POST.dict()
            try:
                result.update(get_session_details(request))
            except Exception as e:
                result["log_error"] = f"Logging exception {type(e)}: {str(e)}"
        return result


    def log_message(self, level, message, request=None):
        result = self.compile_message(message, request)
        if level.upper() == "DEBUG":
            self.logger.debug(result)
        elif level.upper() == "INFO":
            self.logger.info(result)
        elif level.upper() == "WARNING":
            self.logger.warning(result)
        elif level.upper() == "ERROR":
            self.logger.error(result)
        elif level.upper() == "CRITICAL":
            self.logger.critical(result)
        else:
            self.logger.info(result)


    def info(self, message, request=None):
        result = self.compile_message(message, request)
        self.logger.info(result)


    def debug(self, message, request=None):
        result = self.compile_message(message, request)
        ## add request data if it's a debug-level message
        try:
            if hasattr(request, "json") and request.is_json:
                result["data"] = request.json
        except:
            pass
        self.logger.debug(result)


    def warning(self, message, request=None):
        result = self.compile_message(message, request)
        self.logger.warning(result)


    def error(self, message, request=None):
        result = self.compile_message(message, request)
        self.logger.error(result)


    def exception(self, message, request=None):
        result = self.compile_message(message, request)
        self.logger.error(result)


    def critical(self, message, request=None):
        result = self.compile_message(message, request)
        self.logger.critical(result)
