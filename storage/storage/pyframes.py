import os
from threading import Thread

import h5py
from lockfile import LockFile

import numpy as np
import scipy.ndimage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from storage import app

logger = app.logger


def extract_frame(frame_number, frame_type, experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', '{}.h5'.format(experiment_id))
    with h5py.File(frames_file_path, 'r') as frames_file:
        frame = frames_file[frame_type][str(frame_number)]
    logger.info('hdf5 file: extract frame {} of experiment {} successfully'.format(frame_id, experiment_id))
    return frame


def add_frame(frame, frame_info, frame_number, frame_type, frame_id, experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', '{}.h5'.format(experiment_id))

    lock = LockFile(frames_file_path)
    with lock:
        with h5py.File(frames_file_path, 'r+') as frames_file:
            frames_file[frame_type].create_dataset(str(frame_number), data=frame, compression="gzip", compression_opts=4)
            frames_file[frame_type][str(frame_number)].attrs["frame_info"] = frame_info.encode('utf8')

    logger.info('hdf5 file: add frame {} to experiment {} successfully'.format(frame_id, experiment_id))

    png_file_path = os.path.abspath(os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                 str(frame_id) + '.png'))
    Thread(target=make_png, args=(frame, png_file_path)).start()
    logger.info('png: start making png from frame {} of experiment {}'.format(frame_id, experiment_id))


def delete_frame(frame_number, frame_type, frame_id,  experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', '{}.h5'.format(experiment_id))
    with h5py.File(frames_file_path, 'r+') as frames_file:
        del frames_file[frame_type][str(frame_number)]
    logger.info(
        'hdf5 file: frame {} was deleted from experiment {} successfully'.format(str(frame_id), str(experiment_id)))


def make_png(frame, png_path):
    logger.info('Going to make png...')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    enhanced_image = scipy.ndimage.filters.median_filter(np.rot90(frame), size=3)
    im = ax.imshow(enhanced_image, cmap=plt.cm.gray)  # vmin, vmax
    fig.colorbar(im)
    fig.savefig(png_path)
    plt.close(fig)
    logger.info('png was made')
