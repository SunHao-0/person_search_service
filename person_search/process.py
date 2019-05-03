# encoding: utf-8
import logging.config
import net
from cv2 import CAP_PROP_POS_FRAMES
import cv2
import uuid
import scipy.io as si
from _init_env import PERSON_SEARCH_HOME

logger = logging.getLogger(__name__)


def process_video(video_name, person_images):
    # 流程
    # 生成处理方案 [video,step]
    # 数据处理 线性单线程处理
    # 数据存储 mat 存储
    # 返回处理结果
    reader, step, video_identifier = __gen_process_plan(video_name)
    processed_data = __process_data(reader, step)
    person_uuids = __process_person_img(person_images, processed_data)
    __store_local(processed_data, video_identifier)
    return video_identifier, step, processed_data, person_uuids


def generate_trace(video_data):
    person_uuids = video_data["person_uuids"]
    person_mat = [(uui, video_data[uui]["feature"]) for uui in person_uuids]
    frames_feature = video_data["features"][0]  # TODO fix bug
    frames_nos = video_data["frame_no"][0]
    logger.info("Generating trace for [%d] person of [%d] frame_num" % (len(person_mat), len(frames_nos)))
    row_traces = map(lambda person: (person_mat[0], __candidate_frame(person_mat[1], frames_feature, frames_nos)),
                     person_mat)
    trace_map = map(lambda pair: (pair[0], __group(pair[1])), row_traces)
    return trace_map


def __candidate_frame(person, frame_features, frame_nos, th=0.65):
    person = person.reshape(256)
    return [frame_no for feature, frame_no in zip(frame_features, frame_nos)
            if max(feature.dot(person) >= th)]


def __group(frame_nos, step=50):
    result_group = []
    current_group = []
    last_frame = frame_nos[0]
    for frame_no in frame_nos:
        if frame_no - last_frame <= step:
            current_group.append(frame_no)
        else:
            result_group.append(current_group)
            current_group = []
        last_frame = frame_no
    return result_group


def __gen_process_plan(video_name):
    cv2_video_reader = cv2.VideoCapture(video_name)
    is_open, _ = cv2_video_reader.read()  # 试读 预热
    if not is_open:
        raise RuntimeError("No such video:" + video_name)
    step = 500
    video_identifier = str(uuid.uuid1()).replace("-", "")
    logger.debug("Process Plan:\n video_name:%s\n step:%s\n identifier:%s" % (video_name, step, video_identifier))
    return cv2_video_reader, step, video_identifier


def __process_data(video_reader, step):
    dic = {"frame": [], "boxes": [], "features": [], "frame_no": []}
    current_frame, ret = (0, True)
    logger.info("Processing video data ...")
    while ret:
        video_reader.set(CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = video_reader.read()
        if not ret:
            logger.info("Process stop at:%s frame" % str(current_frame))
            break
        boxes, features = net.extract_gallery(frame)
        if boxes is not None:
            dic["frame"].append(frame)
            dic["boxes"].append(boxes)
            dic["features"].append(features)
            dic["frame_no"].append(current_frame)
        current_frame += step
    processed_num = len(dic["frame"])
    logger.info("Video Processed finished: total processed:%s frames" % processed_num)
    return dic


def __process_person_img(person_images, dic):
    logger.info("Person to be processed:%d" % (len(person_images)))
    person_mats = [cv2.imread(person) for person in person_images]
    person_uuids = [str(uuid.uuid1()) for _ in person_images]
    person_mats_features = [{"image": image, "feature": net.extract_probe(image)} for uui, image in
                            zip(person_uuids, person_mats)]
    dic["person_uuids"] = person_uuids
    for uui, mat_feature in zip(person_uuids, person_mats_features):
        dic[uui] = mat_feature
    logger.info("Person processed number:%d" % len(person_mats))
    return person_uuids


def __store_local(data, video_identifier):
    if len(data["frame"]) <= 0:
        logger.warn("Trying to store empty data into local mat")
        return
    import os.path as osp
    video_mat_path = osp.join(PERSON_SEARCH_HOME, "person_search", "output")
    si.savemat(osp.join(video_mat_path, str(video_identifier)), data)
    logger.info("Video mat:[%s] saved to:%s" % (video_identifier, video_mat_path))
    return video_identifier
