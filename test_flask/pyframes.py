import h5py
import os


def extract_frame(frame_id, experiment_id):
    frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    frames_file = h5py.File(frames_file_path, 'r')
    frame = frames_file[str(frame_id)]
    return frame


def add_frame(frame,frame_id, experiment_id):
    frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    frames_file = h5py.File(frames_file_path, 'r+')
    frames_file.create_dataset(str(frame_id), data=frame)
    return


def delete_frame(frame_id, experiment_id):
    frames_file_path = os.path.join('storage', 'experiments', str(experiment_id), 'before_processing', 'frames.h5')
    frames_file = h5py.File(frames_file_path, 'r+')
    del frames_file[str(frame_id)]
    return