#!/usr/bin/python
from flask import Flask, jsonify
from flask import request
import json
import logging

logging.basicConfig(format = u'%(levelname)-8s [%(asctime)s] %(message)s', level = logging.DEBUG, filename = u'stub_webpage.log')


app = Flask(__name__)


@app.route('/stub_webpage', methods=['POST'])
def got_request():
    logging.debug("Something has been recieved...")
    if not request.data:
        logging.debug("- empty\n")
        return jsonify({'result': 'fail'})
    else:
        message = json.loads(request.data)
        if message['type'] == 'message':
            logging.debug('- it is message:')
            logging.debug( message[u'message'] +  "\n")
        elif message[u'type'] == 'frame':
            image_str = message['frame']['image_data']['image']
            logging.debug('- it is image\n')
        else:
            logging.debug('- undefined')
            return jsonify({'result': 'success'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 5021)











