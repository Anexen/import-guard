import json
import logging


def log(message):
    logging.debug(json.dumps(message))
