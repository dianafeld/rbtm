import json
import os
import numpy as np
import h5py

from flask import jsonify, make_response, request, abort, Response, send_file
from bson.json_util import dumps, loads
from bson.objectid import ObjectId

import pymongo as pm

from storage import pyframes
from storage import filesystem as fs
from storage import visualization_3d
from storage import app

from conf import MONGODB_URI

logger = app.logger

# TODO login and pass not secure
client = pm.MongoClient(MONGODB_URI)
#db = client.get_default_database()
db = client["robotom"]


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

    logger.info(b'Request body: ' + request.data)

    find_query = json.loads(request.data.decode())

    experiments = db['experiments']

    cursor = experiments.find(find_query).sort('timestamp', pm.DESCENDING)

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

    logger.info(b'Request body: ' + request.data)

    insert_query = json.loads(request.data.decode())

    experiments = db['experiments']

    experiment_id = insert_query['exp_id']
    insert_query.pop('exp_id', None)
    insert_query['_id'] = experiment_id

    if fs.create_experiment(experiment_id, dumps(insert_query)):
        insert_query['finished'] = False
        experiments.insert(insert_query)

        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'experiment {} already exists in file system'.format(experiment_id)})


@app.route('/storage/experiments/finish', methods=['POST'])
def finish_experiment():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    logger.info(b'Request body: ' + request.data)

    json_msg = json.loads(request.data.decode())

    experiment_id = json_msg['exp_id']

    if json_msg['type'] == 'message':
        if json_msg['message'] == 'Experiment was finished successfully':
            db.experiments.update({'_id': experiment_id},
                                  {'$set': {'finished': True}})
        else:
            logger.warning(json_msg['exception message'] + json_msg['error'])

    return jsonify({'result': 'success'})


@app.route('/storage/frames/post', methods=['POST'])
def new_frame():
    if not (request.files and request.form):
        logger.error('Incorrect format')
        abort(400)

    logger.info('Request body: ' + str(request.form))

    json_frame = json.loads(request.form['data'])
    experiment_id = json_frame['exp_id']

    frame = request.files['file']

    logger.info('Going to np.load...')
    image_array = np.load(frame.stream)['frame_data']
    logger.info('Image array has been loaded!')

    frame_id = db['frames'].insert(json_frame)
    frame_number = str(json_frame['frame']['number'])
    frame_type = str(json_frame['frame']['mode'])
    frame_info = dumps(db['frames'].find({"_id": ObjectId(frame_id)}))

    pyframes.add_frame(image_array, frame_info, frame_number, frame_type, frame_id, experiment_id)

    logger.info('experiment id: {} frame id: {}'.format(str(experiment_id), str(frame_id)))

    return jsonify({'result': 'success'})


@app.route('/storage/frames_info/get', methods=['POST'])
def get_frame_info():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    logger.info(b'Request body: ' + request.data)

    find_query = json.loads(request.data.decode())

    frames = db['frames']

    cursor = frames.find(find_query).sort('frame.number', pm.ASCENDING)

    resp = Response(response=dumps(cursor),
                    status=200,
                    mimetype="application/json")

    return resp


@app.route('/storage/png/get', methods=['POST'])
def get_png():
    if not request.data:
        logger.error('Incorrect format')
        abort(400)

    logger.info(b'Request body: ' + request.data)

    find_query = json.loads(request.data.decode())
    frame_id = find_query['frame_id']
    experiment_id = find_query['exp_id']

    png_file_path = os.path.abspath(os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                 str(frame_id) + '.png'))

    #if not os.path.exists(os.path.join('storage', png_file_path)):
    #if not os.path.exists(png_file_path):
    #    abort(404)

    return send_file(png_file_path, mimetype='image/png')


@app.route('/storage/experiments/<experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    json_result = jsonify({'deleted': 'success'})
    logger.info('Deleting experiment: ' + experiment_id)

    experiments = db['experiments']
    frames = db['frames']

    exp_query = {'_id': experiment_id}
    cursor = experiments.find(exp_query)
    if cursor.count() == 0:
        logger.error('Experiment not found')
    else:
        experiments.remove(exp_query)
        if cursor.count() != 0:
            logger.error("Can't remove experiment")
            json_result = jsonify({'deleted': 'fail'})
        else:
            logger.info("database: deleted experiment {} successfully".format(experiment_id))

    frames_query = {'exp_id': experiment_id}
    frames.remove(frames_query)
    if frames.find(frames_query).count() != 0:
        logger.error("Can't remove frames")
        json_result = jsonify({'deleted': 'fail'})
    else:
        logger.info("database: deleted frames of {} successfully".format(experiment_id))

    fs.delete_experiment(experiment_id)

    # db['reconstructions'].remove(request.get_json())

    return json_result


@app.route('/storage/experiments/<experiment_id>/3d/<int:rarefaction>/<int:level1>/<int:level2>', methods=['GET'])
def get_3d_visualization(experiment_id, rarefaction, level1, level2):
    rarefaction = max(rarefaction, 1)
    level1 = min(max(level1, 0), 25)
    level2 = min(max(level2, 0), 25)
    if level2 < level1:
        level1, level2 = level2, level1

    hfd5_filename = os.path.abspath("data/hand/result.hdf5")
    output_filename = os.path.abspath("data/hand/visualization_3d.hdf5")
    visualization_3d.get_and_save_3d_points(
        hfd5_filename, output_filename, rarefaction, level1, level2)

    return send_file(output_filename, mimetype='application/x-hdf5', 
        as_attachment=True, attachment_filename=str(experiment_id) + '.hdf5')
