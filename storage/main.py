from flask import Flask, jsonify, make_response, request, abort, Response, send_file
from bson.json_util import dumps
from bson.objectid import ObjectId
import pymongo as pm
import pyframes
import filesystem as fs
import json
import logging
import os
import numpy as np
from io import StringIO, BytesIO

app = Flask(__name__)


# TODO login and pass not secure
MONGODB_URI = 'mongodb://admin:33zxcdsa@ds049219.mongolab.com:49219/robotom'
client = pm.MongoClient(MONGODB_URI)
db = client.get_default_database()


# for returning error as json file
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def incorrect_format(error):
    return make_response(jsonify({'error': 'Incorrect format'}), 400)


@app.errorhandler(500)
def incorrect_format(error):
    return make_response(jsonify({'error': 'Internal Server'}), 500)


# return experiments by request json file. return json
@app.route('/storage/experiments/get', methods=['POST'])
def get_experiments():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data.decode())
        logging.debug(find_query)

        experiments = db['experiments']

        if 'select' in find_query and find_query['select'] == 'all':
            cursor = experiments.find()
        else:
            cursor = experiments.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException as e:
        logging.error(e)
        abort(500)


# create new experiment, need json file as request return result:success json if success
@app.route('/storage/experiments/post', methods=['POST'])
def create_experiment():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        experiments = db['experiments']

        insert_query = json.loads(request.data.decode())
        logging.debug(insert_query)
        experiment_id = insert_query['experiment id']

        if fs.create_new_experiment(experiment_id):
            insert_query['finished'] = False
            experiments.insert(insert_query)
            
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'experiment {} already exists in file system'.format(experiment_id)})

    except BaseException as e:
        logging.error(e)
        abort(500)


@app.route('/storage/frames/post', methods=['POST'])
def new_frame():
    if not (request.files and request.form) and not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        if request.data:
            json_frame = json.loads(request.data.decode())
        else:
            logging.debug(request.form)
            logging.debug(request.form['data'])
            json_frame = json.loads(request.form['data'])

        experiment_id = json_frame['exp_id']

        if json_frame['type'] == 'message':
            if json_frame['message'] == 'Experiment was finished successfully':
                db.experiments.update({'_id': ObjectId(experiment_id)}, {'finished': True})
            else:
                logging.warning(json_frame['exception message'] + json_frame['error'])
        elif json_frame['type'] == 'frame':

            frame = request.files['file']

            logging.info('Going to np.load...')
            image_array = np.load(frame.stream)['frame_data']
            logging.info('Image array has been loaded!')
            logging.debug(type(image_array))
            logging.debug(image_array[1])

            frame_id = db['frames'].insert(json_frame)

            pyframes.add_frame(image_array, frame_id, experiment_id)

            logging.info('experiment id: {} frame id: {}'.format(str(experiment_id), str(frame_id)))

    except BaseException as e:
        logging.error(e)
        abort(500)

    return jsonify({'result': 'success'})


@app.route('/storage/frames/get', methods=['POST'])
def get_frame():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        frames = db['frames']
        find_query = json.loads(request.data.decode())
        cursor = frames.find(find_query)
        frames_list = list(cursor)
        for frame in frames_list:
            if frame['type'] == 'frame':
                frame_id = frame['_id']
                experiment_id = frame['exp_id']

                image_numpy = frames.extract_frame(frame_id, experiment_id)

                s = StringIO.StringIO()
                np.savetxt(s, image_numpy, fmt="%d")

                frame['frame']['image_data']['image'] = s.getvalue()
        logging.info('done')
        resp = Response(response=dumps(frames_list),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException as e:
        logging.error(e)
        abort(500)


@app.route('/storage/frames_info/get', methods=['POST'])
def get_frame_info():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        frames = db['frames']
        find_query = json.loads(request.data.decode())
        cursor = frames.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException as e:
        logging.error(e)
        abort(500)


# update data of the experiment, need json file as a request'
@app.route('/storage/experiments/put', methods=['POST'])
def update_experiment():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        experiments = db['experiments']
        query = json.loads(request.data.decode())
        experiment_id = experiments['_id']
        experiments.update({'_id': experiment_id}, query)
    except BaseException as e:
        logging.error(e)
        abort(500)
    return jsonify({'result': 'success'})


# delete data of the experiment, return json file
@app.route('/storage/experiments/delete', methods=['POST'])
def delete_experiment():
    if not request.json:
        logging.error('Incorrect format')
        abort(400)

    try:
        logging.debug(json.loads(request.data.decode()))
        experiments = db['experiments']
        frames = db['frames']

        cursor = experiments.find(json.loads(request.data.decode()))

        experiments.remove(json.loads(request.data.decode()))

        experiments_list = list(cursor)
        for experiment in experiments_list:
            experiment_id = experiment['_id']
            frames.remove({'experiment id': experiment_id})
            fs.delete_experiment(experiment_id)

        # db['reconstructions'].remove(request.get_json())

        return jsonify({'deleted': cursor.count()})

    except BaseException as e:
        logging.error(e)
        abort(500)


@app.route('/storage/png/get', methods=['POST'])
def get_png():
    if not request.data:
        logging.error('Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data.decode())
        frame_id = find_query['id']
        experiment_id = find_query['exp_id']

        png_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                     str(frame_id) + '.png')

        if not os.path.exists(png_file_path):
            abort(404)

        return send_file(png_file_path, mimetype='image/png')

    except Exception as e:
        logging.error(e)
        abort(500)

if __name__ == '__main__':
    logs_path = os.path.join('logs', 'storage.log')
    if not os.path.exists(os.path.dirname(logs_path)):
        os.makedirs(os.path.dirname(logs_path))

    logging.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=logs_path)
    app.run(host='0.0.0.0', port=5006)
