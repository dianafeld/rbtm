import os
import h5py


def create_new_experiment(experiment_id):
    experiment_path = os.path.join('storage', 'experiments', str(experiment_id))
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
    return