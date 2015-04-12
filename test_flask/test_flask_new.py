from flask import Flask, jsonify, make_response, request, abort, Response
from bson.json_util import dumps
import pymongo as pm
import pyframes
import pyfileSystem as fs
import json

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


# return experiments by request json file. return json
@app.route('/storage/experiments', methods=['GET'])
def get_experiments():
    if not request.json:
        abort(400)
    experiments = db['experiments']
    cursor = experiments.find(request.get_json())
    resp = Response(response=dumps(cursor),
                    status=200,
                    mimetype="application/json")

    return resp


# create new experiment, need json file as request return result:success json if success
@app.route('/storage/experiments', methods=['POST'])
def create_experiment():
    if not request.json:
        abort(400)
    experiments = db['experiments']
    insert_query = request.get_json()
    experiment_id = experiments.insert(insert_query)
    fs.create_new_experiment(experiment_id)
    return jsonify({'result': 'success'})


@app.route('/storage/frames', methods=['POST'])
def new_frame():
    if not request.data:
        abort(400)

    json_frame = json.loads(request.data)

    frame = json_frame[u'image_data'][u'image']
    json_frame[u'image_data'].pop(u'image')

    experiment_id = json_frame[u'experiment_id']
    frame_id = db[u'frames'].insert(json_frame)

    pyframes.add_frame(frame, frame_id, experiment_id)

    return jsonify({'result': 'success'})

# update data of the experiment, need json file as a request'
@app.route('/storage', methods=['PUT'])
def update_task(task_id):
    if not request.json:
        abort(400)

    db['experiments'].update(request.get_json())
    return jsonify(request.get_json())

# delete data of the experiment, return json file
@app.route('/storage', methods=['DELETE'])
def delete_experiment():
    if not request.json:
        abort(400)

    cursor = db['experiments'].find(request.get_json())

    db['experiments'].remove(request.get_json())
    db['frames'].remove(request.get_json())
    db['reconstructions'].remove(request.get_json())

    return jsonify({'deleted': cursor.count()})

@app.route('/storage', methods=['GET'])
def get_frame():
    frame = db['frames']
    cursor = frame.find()
    print(list(cursor))
    return jsonify({'frames': list(cursor)})

if __name__ == '__main__':
    app.run(host='0.0.0.0')
