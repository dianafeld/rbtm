import os
import shutil
import h5py

from storage import app
logger = app.logger


def create_experiment(experiment_id):
    experiment_path = os.path.join('data', 'experiments', str(experiment_id))

    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)
        before_processing_path = os.path.join(experiment_path, 'before_processing')
        os.makedirs(before_processing_path)

        png_before_processing_path = os.path.join(before_processing_path, "png")
        os.makedirs(png_before_processing_path)

        after_processing_path = os.path.join(experiment_path, 'after_processing')
        os.makedirs(after_processing_path)

        reconstructions_path = os.path.join(experiment_path, 'reconstructions')
        os.makedirs(reconstructions_path)

        vis_path = os.path.join(experiment_path, '3d')
        os.makedirs(vis_path)

        frames_file_path = os.path.join(before_processing_path, '{}.h5'.format(experiment_id))
        with h5py.File(frames_file_path, 'w') as frames_file:
            frames_file.create_group("empty")
            frames_file.create_group("dark")
            frames_file.create_group("data")

        logger.info('file system: create experiment {} successfully'.format(experiment_id))
        return True
    else:
        logger.warning('file system: experiment {} already exists'.format(experiment_id))
        return False


def delete_experiment(experiment_id):
    experiment_path = os.path.join('data', 'experiments', str(experiment_id))
    if os.path.exists(experiment_path):
        shutil.rmtree(experiment_path)
        logger.info('file system: delete experiment {} successfully'.format(experiment_id))
        return True
    else:
        logger.warning('file system: cant find experiment {} for deleting'.format(experiment_id))
        return False