#!/usr/bin/python

"""
29.11.15 - Rustam
Stub web-page of adjustment for testing module "Experiment" without changing anything more
It just recieves messages from 'experiment' and returns 'success'
Logs to 'stub_webpage.log' file
Launch server on port 5021
"""

from flask import Flask, jsonify
from flask import request
import json
import logging
from socket import error as socket_error

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                    filename=u'experiment/stubs/stub_webpage.log')

app = Flask(__name__)


@app.route('/stub_webpage', methods=['POST'])
def got_request():
    logging.info("Something has been received...")
    if not request.data:
        logging.info("- empty\n")
        return jsonify({'result': 'fail'})
    else:
        message = json.loads(request.data)
        if 'type' not in message.keys():
            logging.info('- it is not message at all')
        else:
            if message['type'] == 'message':
                logging.info('- it is message:')
                logging.info(message['message'] + "\n")
            elif message['type'] == 'frame':
                image_str = message['frame']['image_data']['image']
                logging.info('- it is image\n')
            else:
                logging.info('- undefined')
        return jsonify({'result': 'success', "I'm": "STUB web-page of adjustment", })


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5021)
    except socket_error:
        pass
    # if you don't pass - it will complain "socket.error: [Errno 98] Address already in use"
    # because of twice execution (all files are run twice because of flask reloader, look
    # http://stackoverflow.com/questions/26958952/python-program-seems-to-be-running-twice)
    else:
        print "Stub web-page of adjustment starts to run"
