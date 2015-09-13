import os
import logging

from flask import Flask
app = Flask(__name__)


def logger_setup():
    from logging.handlers import RotatingFileHandler
    from logging import StreamHandler

    logs_path = os.path.join('logs', 'experiment.log')
    if not os.path.exists(os.path.dirname(logs_path)):
        os.makedirs(os.path.dirname(logs_path))

    app.logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(logs_path, maxBytes=512000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - [LINE:%(lineno)d]# - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    stream_handler = StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(stream_handler)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

logger_setup()

import experiment.views
