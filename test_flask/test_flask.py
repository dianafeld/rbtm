from flask import Flask, jsonify, make_response, request, abort, Response
from bson.json_util import dumps
import pymongo

app = Flask(__name__)

MONGODB_URI = 'mongodb://admin:33zxcdsa@ds049219.mongolab.com:49219/robotom'
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_default_database()

#for returning error as json file
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def incorrect_format(error):
    return make_response(jsonify({'error': 'Incorrect format'}), 400)


#now return all experiments as json file
@app.route('/stoarge/experiments', methods=['GET'])
def get_experments():
    experiments = db['experiments']
    cursor = experiments.find()
    print(list(cursor))
    return jsonify({'experiments': list(cursor)})

#create new experiment, need json file as request
@app.route('/stoarge/experiments', methods=['POST'])
def create_experiment():
    if not request.json:
        abort(400)
    db['experiments'].insert(request.get_json())
    print(request.get_json())
    return jsonify(request.get_json())

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

if __name__ == '__main__':
    app.run()