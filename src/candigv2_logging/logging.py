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


def get_auth_token(request):
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


def get_session_details(request):
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


def getLogger(file_name):
    return logging.getLogger(file_name)


def compile_message(message, request):
    result = {"message": message}
    if request is not None:
        if hasattr(request, "path"):
            result["path"] = request.path
        if hasattr(request, "method"):
            result["method"] = request.method
        if hasattr(request, "query_string"):
            result["query"] = request.query_string
        try:
            result.update(get_session_details(request))
        except Exception as e:
            result["log_error"] = f"Logging exception {type(e)}: {str(e)}"
    return result


def log_message(level, message, request=None):
    logger = getLogger(__file__)
    result = compile_message(message, request)
    if level.upper() == "DEBUG":
        logger.debug(result)
    elif level.upper() == "INFO":
        logger.info(result)
    elif level.upper() == "WARNING":
        logger.warning(result)
    elif level.upper() == "ERROR":
        logger.error(result)
    elif level.upper() == "CRITICAL":
        logger.critical(result)
    else:
        logger.info(result)
