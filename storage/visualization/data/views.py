#!/usr/bin/python
# -*- coding: UTF-8 -*-

# for running it on remote machine for uploading data to visualization
# example of data is R50_128G.json

from datetime import timedelta
from flask import make_response, request, current_app
from functools import update_wrapper
from prepare_points import prepare_points


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            #h['Access-Control-Allow-Methods'] = ['POST', 'GET', 'OPTIONS']
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        f.required_methods = ['OPTIONS']
        return update_wrapper(wrapped_function, f)
    return decorator


import json
import time
import os

from flask import request
from flask import Response
from flask import make_response
from flask import send_file
from flask import Flask

app = Flask(__name__)




OBJECT = "hand"


@app.route('/take_json/<path:filename>', methods=['GET'])
@crossdomain(origin='*')
def send_json(filename):
    return send_file("prepared_data/" + OBJECT + "/" + filename)

@app.route('/cut/<int:fil>/<int:rar>/<int:lb>/<int:ub>', methods=['GET'])
@crossdomain(origin='*')
def cut(fil, rar, lb, ub):
    filename = prepare_points(fil, rar, lb, ub, dirname="prepared_data/" + OBJECT + "/")
    #os.system("python prepare_points.py %d %d %f %f" % (fil, rar, lb, ub))
    #filename = "on_server/F%dR%d_L%dU%d.json" % (fil, rar, lb, ub)
    return send_file(filename)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True, port=5001)

#Самая важная часть работы. Использовался язык JavaScript. В конце концов было решено для отрисовки выбрать библиотеку three.js (http://threejs.org/), так как она идёт под лицензией MIT (разрешено свободное использование), а также она широко используется, вследствие чего по ней легко найти информацию в интернете. 

#В начале выбиралось между двумя вариантами отрисовки — нарисовать массив данных как «облако точек» или рисовать с помощью изоповерхностей. Первый вариант более легче и понятнее для реализации, поэтому в итоге выбор остался на нём.

