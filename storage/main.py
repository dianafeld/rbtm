from flask import Flask, jsonify, make_response, request, abort, Response, send_file
from bson.json_util import dumps
import pymongo as pm
import json
import logging
import os
import numpy as np

import pyframes
import filesystem as fs

app = Flask(__name__)


def logger_setup():
    from logging.handlers import RotatingFileHandler

    logs_path = os.path.join('logs', 'storage.log')
    if not os.path.exists(os.path.dirname(logs_path)):
        os.makedirs(os.path.dirname(logs_path))

    app.logger.setLevel(logging.DEBUG)
    file_handler = RotatingFileHandler(logs_path, maxBytes=10000, backupCount=1)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - [LINE:%(lineno)d]# - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.DEBUG)
    log.addHandler(file_handler)

logger_setup()
logger = app.logger


# TODO login and pass not secure
MONGODB_URI = 'mongodb://admin:33zxcdsa@ds049219.mongolab.com:49219/robotom'
client = pm.MongoClient(MONGODB_URI)
db = client.get_default_database()


# for returning error as json file
@app.errorhandler(404)
def not_found(exception):
    logger.exception(exception)
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def incorrect_format(exception):
    logger.exception(exception)
    return make_response(jsonify({'error': 'Incorrect format'}), 400)


@app.errorhandler(500)
def incorrect_format(exception):
    logger.exception(exception)
    return make_response(jsonify({'error': 'Internal Server'}), 500)


# return experiments by request json file. return json
@app.route('/storage/experiments/get', methods=['POST'])
def get_experiments():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    find_query = json.loads(request.data.decode())
    logger.info(find_query)

    experiments = db['experiments']

    cursor = experiments.find(find_query)

    resp = Response(response=dumps(cursor),
                    status=200,
                    mimetype="application/json")

    return resp



# create new experiment, need json file as request return result:success json if success
@app.route('/storage/experiments/create', methods=['POST'])
def create_experiment():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    try:
        experiments = db['experiments']

        insert_query = json.loads(request.data.decode())
        logger.info(insert_query)
        experiment_id = insert_query['exp_id']
        insert_query.pop('exp_id', None)
        insert_query['_id'] = experiment_id

        if fs.create_new_experiment(experiment_id):
            insert_query['finished'] = False
            experiments.insert(insert_query)

            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'experiment {} already exists in file system'.format(experiment_id)})

    except BaseException as e:
        logger.error(e)
        abort(500)


@app.route('/storage/experiments/finish', methods=['POST'])
def finish_experiment():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    try:
        json_msg = json.loads(request.data.decode())
        logger.info(json_msg)

        experiment_id = json_msg['exp_id']

        if json_msg['type'] == 'message':
            if json_msg['message'] == 'Experiment was finished successfully':
                db.experiments.update({'_id': experiment_id},
                                      {'$set': {'finished': True}})
            else:
                logger.warning(json_msg['exception message'] + json_msg['error'])

    except BaseException as e:
        logger.error(e)
        abort(500)

    return jsonify({'result': 'success'})


@app.route('/storage/frames/post', methods=['POST'])
def new_frame():
    if not (request.files and request.form):
        logger.error('Incorrect format')
        abort(400)

    try:
        logger.debug(request.form)
        json_frame = json.loads(request.form['data'])
        experiment_id = json_frame['exp_id']

        frame = request.files['file']

        logger.info('Going to np.load...')
        image_array = np.load(frame.stream)['frame_data']
        logger.info('Image array has been loaded!')
        logger.debug(type(image_array))
        logger.debug(image_array[1])

        frame_id = db['frames'].insert(json_frame)

        pyframes.add_frame(image_array, frame_id, experiment_id)

        logger.info('experiment id: {} frame id: {}'.format(str(experiment_id), str(frame_id)))

    except BaseException as e:
        logger.error(e)
        abort(500)

    return jsonify({'result': 'success'})


@app.route('/storage/frames_info/get', methods=['POST'])
def get_frame_info():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    try:
        logger.info(request.data.decode())
        frames = db['frames']
        find_query = json.loads(request.data.decode())
        cursor = frames.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException as e:
        logger.error(e)
        abort(500)


@app.route('/storage/png/get', methods=['POST'])
def get_png():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data.decode())
        frame_id = find_query['frame_id']
        experiment_id = find_query['exp_id']

        png_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                     str(frame_id) + '.png')

        if not os.path.exists(png_file_path):
            abort(404)

        return send_file(png_file_path, mimetype='image/png')

    except RuntimeError as e:
        logger.error(e)
        abort(500)


# Needs rewriting
# @app.route('/storage/frames/get', methods=['POST'])
# def get_frame():
#     if not request.data:
#         logger.error('Incorrect format')
#         abort(400)
#
#     try:
#         frames = db['frames']
#         find_query = json.loads(request.data.decode())
#         cursor = frames.find(find_query)
#         frames_list = list(cursor)
#         for frame in frames_list:
#             if frame['type'] == 'frame':
#                 frame_id = frame['_id']
#                 experiment_id = frame['exp_id']
#
#                 image_numpy = frames.extract_frame(frame_id, experiment_id)
#
#                 s = StringIO.StringIO()
#                 np.savetxt(s, image_numpy, fmt="%d")
#
#                 frame['frame']['image_data']['image'] = s.getvalue()
#         logger.info('done')
#         resp = Response(response=dumps(frames_list),
#                         status=200,
#                         mimetype="application/json")
#
#         return resp
#
#     except BaseException as e:
#         logger.error(e)
#         abort(500)

# # update data of the experiment, need json file as a request'
# @app.route('/storage/experiments/update', methods=['POST'])
# def update_experiment():
#     if not request.data:
#         logger.error('Incorrect format')
#         abort(400)
#
#     try:
#         experiments = db['experiments']
#         query = json.loads(request.data.decode())
#         experiment_id = experiments['_id']
#         experiments.update({'_id': experiment_id}, query)
#     except BaseException as e:
#         logger.error(e)
#         abort(500)
#     return jsonify({'result': 'success'})


# # delete data of the experiment, return json file
# @app.route('/storage/experiments/delete', methods=['POST'])
# def delete_experiment():
#     if not request.json:
#         logger.error('Incorrect format')
#         abort(400)
#
#     try:
#         logger.debug(json.loads(request.data.decode()))
#         experiments = db['experiments']
#         frames = db['frames']
#
#         cursor = experiments.find(json.loads(request.data.decode()))
#
#         experiments.remove(json.loads(request.data.decode()))
#
#         experiments_list = list(cursor)
#         for experiment in experiments_list:
#             experiment_id = experiment['_id']
#             frames.remove({'experiment id': experiment_id})
#             fs.delete_experiment(experiment_id)
#
#         # db['reconstructions'].remove(request.get_json())
#
#         return jsonify({'deleted': cursor.count()})
#
#     except BaseException as e:
#         logger.error(e)
#         abort(500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)
