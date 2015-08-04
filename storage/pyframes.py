import h5py
import os
import logging
# import pylab as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

from main import app
logger = app.logger


def extract_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r') as frames_file:
            frame = frames_file[str(frame_id)]
        return frame
    except Exception as e:
        logger.error(e)
        return


def add_frame(frame, frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r+') as frames_file:
            frames_file.create_dataset(str(frame_id), data=frame)
        logger.info('hdf5 file: add frame {} to experiment {} successfully'.format(frame_id, experiment_id))

        png_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                     str(frame_id) + '.png')
        make_png(frame, png_file_path)
        logger.info('png: png was made from frame {} of experiment {}'.format(frame_id, experiment_id))
    except BaseException as e:
        logger.error(e)
    return


def delete_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r+') as frames_file:
            del frames_file[str(frame_id)]
        logger.info('hdf5 file: delete frame {} from experiment {} successfully'.format(str(frame_id), str(experiment_id)))
    except BaseException as e:
        logger.error(e)
    return


def make_png(res, frame_path):
    logger.info('Going to make png...')
    small_res = zoom(res, zoom=0.25, order=2)
    plt.imsave(frame_path, small_res, cmap=plt.cm.gray)
    logger.info('png was made')
