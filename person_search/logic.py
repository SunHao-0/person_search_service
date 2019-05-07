import _init_env
from persistence import persist_process_task
from process import process_task
from task_generator import generate_task


def search(video_paths, person_image_paths, step=50):
    """
    Process videos by step and person_images,calculate trace of each person,
    persist result in database
    :param video_paths: each video's local path
    :param person_image_paths: each person image's local path
    :param step: decide how to choose frames in video, 50 for default
    :return: no return
    """
    task_descriptor = generate_task(video_paths, person_image_paths, step)
    processed_task_data = process_task(task_descriptor)
    persist_process_task(task_descriptor, processed_task_data)
