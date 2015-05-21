import h5py
import os
import logging
#import pylab as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

logs_path = os.path.join('logs', 'storage_log.log')
logging.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.DEBUG,
                    filename=logs_path)


def extract_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        frames_file = h5py.File(frames_file_path, 'r')
        frame = frames_file[str(frame_id)][()]
        return frame
    except BaseException, e:
            logging.error(e)
            return




def add_frame(frame, frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        frames_file = h5py.File(frames_file_path, 'r+')
        frames_file.create_dataset(str(frame_id), data=frame)
        logging.info(u'hdf5 file: add frame '+str(frame_id)+u' to experiment '+str(experiment_id)+u' successfully')
    except BaseException, e:
        logging.error(e)
    return




def delete_frame(frame_id, experiment_id):
    try:
        frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
        frames_file = h5py.File(frames_file_path, 'r+')
        del frames_file[str(frame_id)]
        logging.info(u'hdf5 file: delete frame ' + str(frame_id) + u' from experiment ' + str(experiment_id) + u' successfully')
    except BaseException, e:
        logging.error(e)
    return


def make_png(res):
    plt.ioff()
    plt.figure()
    plt.imshow(res, cmap=plt.cm.gray)
    plt.colorbar()
    plt.savefig('data.png', bbox_inches='tight')
    