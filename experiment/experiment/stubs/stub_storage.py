#!/usr/bin/python

from __future__ import print_function

"""
29.11.15 - Rustam
Stub storage for testing module "Experiment" without changing anything more
It just recieves messages from 'experiment' and returns 'success'
Logs to 'stub_storage.log' file
Launch server on port 5020
"""

import logging
from socket import error as socket_error

from flask import Flask, jsonify

logging.basicConfig(format=u'%(levelname)-8s [%(asctime)s] %(message)s', level=logging.DEBUG,
                    filename=u'experiment/stubs/stub_storage.log')

app = Flask(__name__)


@app.route('/stub_storage', methods=['POST'])
def got_request():
    logging.info("Something has been recieved...")
    return jsonify({'result': 'success', "I'm": "STUB storage", })


'''
    if not (request.data or request.form):
        logging.info("- empty\n")
        return jsonify({'result': 'fail'})
    else:
        """
        message = json.loads(request.data)
        if 'type' not in message.keys():
            logging.info('- it is not message at all')
        else:
            if message['type'] == 'message':
                logging.info('- it is message:')
                logging.info( message['message'] +  "\n")
            elif message['type'] == 'frame':
                image_str = message['frame']['image_data']['image']
                logging.info('- it is image\n')
            else:
                logging.info('- undefined')
        """
'''
# commented 30.11.15 (Rustam) when try to send here images from "Experiment" and have problems with it

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5020)
    except socket_error:
        pass
    # if you don't pass - it will complain "socket.error: [Errno 98] Address already in use"
    # because of twice execution (all files are run twice because of flask reloader, look
    # http://stackoverflow.com/questions/26958952/python-program-seems-to-be-running-twice)
    else:
        print("Stub storage starts to run")
