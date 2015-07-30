import h5py
import os
import logging
# import pylab as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# logs_path = os.path.join('logs', 'storage.log')
# logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
#                     level=logging.DEBUG,
#                     filename=logs_path)


def extract_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r') as frames_file:
            frame = frames_file[str(frame_id)]
        return frame
    except Exception as e:
        logging.error(e)
        return


def add_frame(frame, frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r+') as frames_file:
            frames_file.create_dataset(str(frame_id), data=frame)
        logging.info('hdf5 file: add frame {} to experiment {} successfully'.format(frame_id, experiment_id))

        png_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'png',
                                     str(frame_id) + '.png')
        make_png(frame, png_file_path)
        logging.info('png: png was made from frame {} of experiment {}'.format(frame_id, experiment_id))
    except BaseException as e:
        logging.error(e)
    return


def delete_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('data', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        with h5py.File(frames_file_path, 'r+') as frames_file:
            del frames_file[str(frame_id)]
        logging.info('hdf5 file: delete frame {} from experiment {} successfully'.format(str(frame_id), str(experiment_id)))
    except BaseException as e:
        logging.error(e)
    return


def make_png(res, frame_path):
    plt.ioff()
    plt.figure()
    plt.imshow(res, cmap=plt.cm.gray)
    plt.colorbar()
    plt.savefig(frame_path, bbox_inches='tight')
    plt.close()
