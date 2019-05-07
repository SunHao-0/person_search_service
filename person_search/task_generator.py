import uuid


def generate_identifier():
    return str(uuid.uuid1()).replace("-", "")


def generate_task(video_paths, person_image_paths, step):
    task_identifier = generate_identifier()
    task_descriptor = {
        "identifier": task_identifier,
        "step": step,
        "videos": {generate_identifier(): path for path in video_paths},
        "person": {generate_identifier(): path for path in person_image_paths}
    }
    return task_descriptor


