import h5py
import os
# import pylab as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import zoom

from storage import app
logger = app.logger


def extract_frame(frame_id, experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    with h5py.File(frames_file_path, 'r') as frames_file:
        frame = frames_file[str(frame_id)]
    logger.info('hdf5 file: extract frame {} of experiment {} successfully'.format(frame_id, experiment_id))
    return frame


def add_frame(frame, frame_id, experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    with h5py.File(frames_file_path, 'r+') as frames_file:
        frames_file.create_dataset(str(frame_id), data=frame)
    logger.info('hdf5 file: add frame {} to experiment {} successfully'.format(frame_id, experiment_id))

    png_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                 str(frame_id) + '.png')
    make_png(frame, png_file_path)
    logger.info('png: png was made from frame {} of experiment {}'.format(frame_id, experiment_id))


def delete_frame(frame_id, experiment_id):
    frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    with h5py.File(frames_file_path, 'r+') as frames_file:
        del frames_file[str(frame_id)]
    logger.info('hdf5 file: frame {} was deleted from experiment {} successfully'.format(str(frame_id), str(experiment_id)))


def make_png(res, frame_path):
    logger.info('Going to make png...')
    small_res = zoom(res, zoom=0.25, order=2)
    plt.imsave(frame_path, small_res, cmap=plt.cm.gray)
    logger.info('png was made')
