from flask import Flask, jsonify, make_response, request, abort, Response
from bson.json_util import dumps
import pymongo as pm
import pyframes
import pyfileSystem as fs
import json
import logging

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
        logging.error(u'Incorrect format')
        abort(400)

    try:
        find_query = json.loads(request.data)

        experiments = db[u'experiments']

        if find_query[u'select'] == u'all':
            cursor = experiments.find()
        else:
            cursor = experiments.find(find_query)

        resp = Response(response=dumps(cursor),
                        status=200,
                        mimetype="application/json")

        return resp

    except ValueError, e:
        logging.error(e)
        abort(500)




# create new experiment, need json file as request return result:success json if success
@app.route('/storage/experiments/post', methods=['POST'])
def create_experiment():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    experiments = db[u'experiments']

    try:
        insert_query = json.loads(request.data)

        insert_query[u'finished'] = False
        experiment_id = experiments.insert(insert_query)
        fs.create_new_experiment(experiment_id)

    except ValueError, e:
        logging.error(e)
        abort(500)

    return jsonify({'result': 'success'})




@app.route('/storage/frames/post', methods=['POST'])
def new_frame():
    if not request.data:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        json_frame = json.loads(request.data)
        experiment_id = json_frame[u'experiment_id']

        if json_frame[u'progress'] == u'finished':
            db.experiments.update({u'_id': experiment_id}, {u'finished': True})
        else:
            frame = json_frame[u'image_data'][u'image']
            json_frame[u'image_data'].pop(u'image')

            frame_id = db[u'frames'].insert(json_frame)

            logging.info(u'experiment_id: ' + experiment_id + u'frame_id: ' + frame_id)

            pyframes.add_frame(frame, frame_id, experiment_id)

    except ValueError, e:
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
            frame_id = frame[u'_id']
            experiment_id = frame[u'experiment_id']
            frame[u'image_data'][u'image'] = pyframes.extract_frame(frame_id, experiment_id)

        resp = Response(response=dumps(frames_list),
                        status=200,
                        mimetype="application/json")

        return resp

    except ValueError, e:
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
    except ValueError, e:
        logging.error(e)
        abort(500)
    return jsonify({'result': 'success'})




# delete data of the experiment, return json file
@app.route('/storage/experiments/delete', methods=['DELETE'])
def delete_experiment():
    if not request.json:
        logging.error(u'Incorrect format')
        abort(400)

    try:
        cursor = db['experiments'].find(request.get_json())

        db['experiments'].dbremove(request.get_json())
        experiment_id = db.experiments[u'_id']
        db['frames'].remove({u'experiment_id': experiment_id})

        # db['reconstructions'].remove(request.get_json())

        fs.delete_experiment(experiment_id)
        
        return jsonify({'deleted': cursor.count()})

    except ValueError, e:
            logging.error(e)
            abort(500)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
