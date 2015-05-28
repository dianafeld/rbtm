#!/usr/bin/python
from flask import Flask, jsonify, make_response, request, abort, Response, send_file
from bson.json_util import dumps
import pymongo as pm
import pyframes
import pyfileSystem as fs
import json
import logging
import os
import numpy as np
import csv
from StringIO import StringIO

app = Flask(__name__)

logs_path = os.path.join('logs', 'storage_log.log')
logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG,
                    filename=logs_path)


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
        logging.error(u'Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data)
        logging.debug(find_query)

        experiments = db[u'experiments']

        if u'select' in find_query and find_query[u'select'] == u'all':
            cursor = experiments.find()
        else:
            cursor = experiments.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException, e:
        logging.error(e)
        abort(500)



# create new user, need json file as request return result:success json if success
@app.route('/storage/users/post', methods=['POST'])
def create_user():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        user = db[u'users']
        query = json.loads(request.data)
        user.insert(query)

    except ValueError, e:
        logging.error(e)
        abort(500)

    return jsonify({'result': 'success'})


@app.route('/storage/users/get', methods=['POST'])
def find_user():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)
    try:
        users = db[u'users']
        find_query = json.loads(request.data)
        logging.info(find_query)

        if u'select' in find_query and find_query[u'select'] == u'all':
            cursor = users.find()
        else:
            cursor = users.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except ValueError, e:
        logging.error(e)
        abort(500)



# update informations about user, return json file
@app.route('/storage/users/update', methods=['POST'])
def update_users():
    if not request.json:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        users = db[u'users']
        find_query = json.loads(request.data)
        logging.info(find_query)

        cursor = users.find(find_query)
        users.update({'user':find_query['user']}, find_query)

        return jsonify({'updated': cursor.count()})

    except BaseException, e:
            logging.error(e)
            abort(500)



# delete user, return json file
@app.route('/storage/users/delete', methods=['POST'])
def delete_users():
    if not request.json:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        users = db[u'users']
        find_query = json.loads(request.data)
        logging.info(find_query)

        cursor = users.find(find_query)
        users.remove(find_query)

        return jsonify({'deleted': cursor.count()})

    except BaseException, e:
            logging.error(e)
            abort(500)



# create new experiment, need json file as request return result:success json if success
@app.route('/storage/experiments/post', methods=['POST'])
def create_experiment():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        experiments = db[u'experiments']

        insert_query = json.loads(request.data)
        logging.debug(insert_query)
        experiment_id = insert_query[u'experiment id']

        if (fs.create_new_experiment(experiment_id)==True):
            insert_query[u'finished'] = False
            experiments.insert(insert_query)
            
            return jsonify({u'result': u'success'})
        else:
            return jsonify({u'result': u'experiment '+str(experiment_id)+u' already exists in file system'})

    except BaseException, e:
        logging.error(e)
        abort(500)




@app.route('/storage/frames/post', methods=['POST'])
def new_frame():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        json_frame = json.loads(request.data)
        experiment_id = json_frame[u'exp_id']

        if json_frame[u'type'] == u'message':
            if json_frame[u'message'] == u'Experiment was finished successfully':
                db.experiments.update({u'_id': experiment_id}, {u'finished': True})
            else:
                logging.WARNING(json_frame[u'exception message'] + json_frame[u'error'])
        elif json_frame[u'type'] == u'frame':
            frame = json_frame[u'frame'][u'image_data'][u'image']
            json_frame[u'frame'][u'image_data'].pop(u'image')
            frame_id = db[u'frames'].insert(json_frame)
            print(1)
            #a = frame.split('\n')
            print(2)
            #reader = csv.reader(frame, delimiter=' ')
            #arr = []
            #for lst in a:
            #    arr.append(lst.split( ))
            #print(3)
            #image_list = list(reader)
            #print(4)
            #del arr[-1]
            #array = np.asarray(arr, dtype=np.int16)
            
            s = StringIO(frame)
            array = np.loadtxt(s, dtype=np.int16)

            print(5)

            #print (array)

            logging.info(u'experiment id: ' + str(experiment_id) + u'frame id: ' + str(frame_id))

            pyframes.add_frame(array , frame_id, experiment_id)

    except BaseException, e:
        logging.error(e)
        abort(500)

    return jsonify({'result': 'success'})




@app.route('/storage/frames/get', methods=['POST'])
def get_frame():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        frames = db[u'frames']
        find_query = json.loads(request.data)
        cursor = frames.find(find_query)
        frames_list = list(cursor)
        for frame in frames_list:
            if frame[u'type']== u'frame':
                frame_id = frame[u'_id']
                experiment_id = frame[u'exp_id']

                image_numpy = pyframes.extract_frame(frame_id, experiment_id)

                tmp_list_of_strs = []
                for lst in image_numpy.tolist():
                    tmp_list_of_strs.append(' '.join(map(str,lst)))
                image_str = '\n'.join(tmp_list_of_strs)

                frame[u'frame'][u'image_data'][u'image'] = image_str
        logging.info('done')
        resp = Response(response=dumps(frames_list),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException, e:
        logging.error(e)
        abort(500)


@app.route('/storage/frames_info/get', methods=['POST'])
def get_frame_info():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        frames = db[u'frames']
        find_query = json.loads(request.data)
        cursor = frames.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except BaseException, e:
        logging.error(e)
        abort(500)





# update data of the experiment, need json file as a request'
@app.route('/storage/experiments/put', methods=['POST'])
def update_experiment():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        experiments = db[u'experiments']
        query = json.loads(request.data)
        experiment_id = experiments[u'_id']
        experiments.update({u'_id': experiment_id}, query)
    except BaseException, e:
        logging.error(e)
        abort(500)
    return jsonify({'result': 'success'})




# delete data of the experiment, return json file
@app.route('/storage/experiments/delete', methods=['POST'])
def delete_experiment():
    if not request.json:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        logging.debug(json.loads(request.data))
        experiments = db[u'experiments']
        frames = db[u'frames']

        cursor = experiments.find(json.loads(request.data))

        experiments.remove(json.loads(request.data))

        experiments_list = list(cursor)
        for experiment in experiments_list:
            experiment_id = experiment[u'_id']
            frames.remove({u'experiment id': experiment_id})
            fs.delete_experiment(experiment_id)

        # db['reconstructions'].remove(request.get_json())


        return jsonify({'deleted': cursor.count()})

    except BaseException, e:
            logging.error(e)
            abort(500)

@app.route('/storage/png/get', methods=['POST'])
def get_png():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data)
        frame_id = find_query[u'id']
        experiment_id = find_query[u'exp_id']
        logging.debug('1')
        frame = pyframes.extract_frame(frame_id, experiment_id)
        print(type(frame))
        pyframes.make_png(frame, frame_id)
        return send_file(str(frame_id) + '.png', mimetype='image/png')

    except StandardError, e:
        logging.error(e)
        abort(500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)