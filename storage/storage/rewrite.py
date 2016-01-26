__author__ = 'arlen'
import os
import h5py

from bson.json_util import dumps, loads
from bson.objectid import ObjectId

#from flask import Flask
#app = Flask(__name__)

from storage import app

from conf import MONGODB_URI

import pymongo as pm

#MONGODB_URI = 'mongodb://database:27017'

# TODO login and pass not secure
client = pm.MongoClient(MONGODB_URI)
#db = client.get_default_database()
db = client["robotom"]

logger = app.logger


def rewrite_file_h5(file):
    old_data = h5py.File(file, "r")
    logger.debug("hdf5: open file " + file)

    experiment_id = os.path.basename(os.path.dirname(os.path.dirname(file)))
    logger.debug(experiment_id)
    new_data_path = os.path.abspath(os.path.join(os.path.dirname(file), experiment_id))
    if not os.path.exists(new_data_path):
        data = h5py.File(os.path.abspath(os.path.join(os.path.dirname(file), experiment_id)))

        experiments = db['experiments']
        experiment_info = dumps(experiments.find({"_id": experiment_id}))
        data.attrs.create("exp_info", experiment_info.encode('utf8'))

        data.create_group("empty")
        data.create_group("dark")
        data.create_group("data")
        logger.debug("hdf5: created groups")

        frames = db['frames']
        for frame_id in old_data.keys():
            frame_info = dumps(frames.find({"_id": ObjectId(frame_id)}))
            json_frame = loads(frame_info)
            frame_number = str(json_frame[0]['frame']['number'])
            frame_type = str(json_frame[0]['frame']['mode'])
            frame_dataset = data[frame_type].create_dataset(frame_number, data=old_data[frame_id], compression="gzip", compression_opts=9)
            frame_dataset.attrs.create("frame_info", frame_info.encode('utf8'))

        print("hdf5: wrote compressed datasets")
        logger.debug("hdf5: wrote compressed datasets")
        data.flush()
        data.close()
    else:
        logger.debug("file already exists")


experiments_path = os.path.join('data', 'experiments')
for root, dirs, files in os.walk(experiments_path):
    for name in files:
       if name == 'frames.h5':
           rewrite_file_h5(os.path.join(root, name))
