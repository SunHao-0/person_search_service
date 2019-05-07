# encoding: utf-8
import logging

import cv2
from cv2 import CAP_PROP_POS_FRAMES

import net

logger = logging.getLogger(__name__)


def process_task(task_descriptor):
    # task:{"identifier": ..., videos:{{"identifier":path} ... },person:{{"..":..}} }
    task_identifier = task_descriptor["identifier"]
    logger.info("Start processing task:%s" % task_identifier)
    video_task = task_descriptor["videos"]
    step = task_descriptor["step"] if "step" in task_descriptor else 50
    processed_video = process_video_task(video_task, step)
    person_task = task_descriptor["person"]
    processed_person = process_person_task(person_task)
    person_trace = process_trace(processed_video, step, processed_person)
    logger.info("Processing finished")
    return {"identifier": task_identifier,
            "step": step,
            "processed_videos": processed_video,
            "processed_person": processed_person,
            "trace": person_trace}


def process_video_task(video_task, step):
    processed_video = {}
    logger.info("Start processing video task,total task [%d] video(s)" % (len(video_task)))
    for video_identifier in video_task:
        video_path = video_task[video_identifier]
        processed_data = process_video(video_path, step)
        # store_mat(processed_data, video_identifier)
        processed_video[video_identifier] = processed_data
    logger.info("Video task processed finished")
    return processed_video


def process_person_task(person_task):
    logger.info("Start processing person task, total person:%d" % len(person_task))
    processed_data = {identifier: process_person_image(person_task[identifier])
                      for identifier in person_task}
    logger.info("Person processing finished")
    return processed_data


def process_video(video_name, step):
    video_reader = cv2.VideoCapture(video_name)
    is_open, _ = video_reader.read()  # 试读 预热
    if not is_open:
        raise RuntimeError("No such video:" + video_name)
    dic = {"boxes": [], "features": [], "frame_nos": []}  # "frame": [],
    current_frame, ret = (0, True)
    logger.info("Processing video: [%s] ..." % video_name)
    while ret:
        video_reader.set(CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = video_reader.read()
        if not ret:
            break
        boxes, features = net.extract_gallery(frame)
        if boxes is not None:
            # dic["frame"].append(frame)
            dic["boxes"].append(boxes)
            dic["features"].append(features)
            dic["frame_nos"].append(current_frame)
        current_frame += step
    processed_num = len(dic["features"])
    logger.info("Video Processed finished: total processed:%s frames" % processed_num)
    return dic


def process_person_image(person_image):
    im = cv2.imread(person_image)
    logger.info("[%s] processed" % person_image)
    return net.extract_probe(im)


def process_trace(processed_videos, step, processed_person):
    logger.info("Start processing trace")
    if len(processed_videos) == 0:
        logger.warning("NO TRACE GENERATED,PROCESSED VIDEO DATA IS EMPTY")
        return {}
    # processed_video{"identifier":data}
    trace_map = {person_identifier: {video_identifier: [] for video_identifier in processed_videos}
                 for person_identifier in processed_person}
    for video_identifier in processed_videos:
        part_trace = generate_video_trace(processed_videos[video_identifier], processed_person, step)
        for person_identifier, t in part_trace:
            trace_map[person_identifier][video_identifier].extend(t)
    info = {
        person_identifier:
            {video_identifier: len(trace_map[person_identifier][video_identifier])
             for video_identifier in trace_map[person_identifier]}
        for person_identifier in trace_map}
    logger.info("Trace generated finished, info:\n%s" % info)
    return trace_map


def generate_video_trace(video_data, person_mat, step):
    person_uuids = person_mat.keys()
    # TODO fix index,currently this function can only work with process video
    person_mat = [(uui, person_mat[uui]) for uui in person_uuids]
    frames_feature = video_data["features"]  # TODO fix bug
    frames_nos = video_data["frame_nos"]
    if len(frames_nos) == 0:
        logger.warning("Trying to generate trace on empty video data")
        return []
    logger.info("Generating trace for [%d] person of [%d] frame_num" % (len(person_mat), len(frames_nos)))
    row_traces = map(lambda person: (person[0], __candidate_frame(person[1], frames_feature, frames_nos)),
                     person_mat)
    trace_map = map(lambda pair: (pair[0], __group(pair[1], step)), row_traces)
    return trace_map


def __candidate_frame(person, frame_features, frame_nos, th=0.65):
    person = person.reshape(256)
    return [frame_no for feature, frame_no in zip(frame_features, frame_nos)
            if max(feature.dot(person) >= th)]


def __group(frame_nos, step=50):
    result_group = []
    if len(frame_nos) == 0:
        return result_group
    start = frame_nos[0]
    last_frame = start
    for frame_no in frame_nos:
        if frame_no - last_frame > step:
            result_group.append([start, last_frame])
            start = frame_no
        last_frame = frame_no
    return result_group


if __name__ == "__main__":
    # test_process_person_image()
    pass
