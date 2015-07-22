import os
import shutil
import h5py
import logging

#logs_path = os.path.join('logs', 'storage.log')
#logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
#                    level=logging.DEBUG,
#                    filename=logs_path)


def create_new_experiment(experiment_id):
    experiment_path = os.path.join('data', 'experiments', str(experiment_id))
        
    try:
        if not os.path.exists(experiment_path):
            os.makedirs(experiment_path)
            before_processing_path = os.path.join(experiment_path, 'before_processing')
            os.makedirs(before_processing_path)

            after_processing_path = os.path.join(experiment_path, 'after_processing')
            os.makedirs(after_processing_path)

            reconstructions_path = os.path.join(experiment_path, 'reconstructions')
            os.makedirs(reconstructions_path)

            frames_file_path = os.path.join(before_processing_path, 'frames.h5')
            h5py.File(frames_file_path, 'w')

            logging.info(u'file system: create experiment '+str(experiment_id)+u' successfully')
            return True
        else:
            logging.warning(u'file system: experiment '+str(experiment_id)+u' already exists')
            return False
    except BaseException, e:
        logging.error(e)


def delete_experiment(experiment_id):
    experiment_path = os.path.join('data', 'experiments', str(experiment_id))
    if os.path.exists(experiment_path):
        try:
            shutil.rmtree(experiment_path)
            logging.INFO(u'file system: delete experiment '+str(experiment_id)+u' successfully')
            return True
        except BaseException, e:
            logging.error(e)
            return False
    else:
        logging.warning(u'file system: cant find experiment '+str(experiment_id)+u'for deleting')
        return False