# encoding: utf-8
from _init_env import PERSON_SEARCH_HOME
import _init_env
import os.path as osp
from fast_rcnn.test_gallery import _im_detect
from fast_rcnn.nms_wrapper import nms
from fast_rcnn.config import cfg, cfg_from_file, cfg_from_list, cfg
from fast_rcnn.test_probe import _im_exfeat
import logging
import caffe
import numpy as np

base = osp.join(PERSON_SEARCH_HOME, "person_search", "net")
cfg_path = osp.join(base, "resnet50.yml")
probe_path = osp.join(base, "eval_probe.prototxt")
gallery_path = osp.join(base, "eval_gallery.prototxt")
model_path = osp.join(base, "resnet50_iter_50000.caffemodel")
# buf
probe_net = None
gallery_net = None

logger = logging.getLogger(__name__)


def __load_net(net_path):
    global model_path, cfg_path
    cfg_from_file(cfg_path)
    caffe.set_mode_gpu()
    caffe.set_device(0)
    return caffe.Net(str(net_path), str(model_path), caffe.TEST)


def extract_probe(query_img, blob_name="feat"):
    global gallery_net, probe_net, probe_path, model_path
    if gallery_net is not None:
        del gallery_net
    probe_net = probe_net or __load_net(probe_path)
    query_roi = [0, 0, query_img.shape[1], query_img.shape[0]]
    query_roi = np.asarray(query_roi).astype(np.float32).reshape(1, 4)
    feature = _im_exfeat(probe_net, query_img, query_roi, [blob_name])
    return np.asarray(feature[blob_name].squeeze())


def extract_gallery(gallery_img, blob_name="feat"):
    global gallery_net, probe_net, gallery_path, model_path
    if probe_net is not None:
        del probe_net
    gallery_net = gallery_net or __load_net(gallery_path)
    threshold = 0.5
    boxes, scores, feat_dic = _im_detect(
        gallery_net, gallery_img, None, [blob_name])
    j = 1
    inds = np.where(scores[:, j] > threshold)[0]
    cls_scores = scores[inds, j]
    cls_boxes = boxes[inds, j * 4:(j + 1) * 4]
    boxes = np.hstack(
        (cls_boxes, cls_scores[:, np.newaxis])).astype(np.float32)
    keep = nms(boxes, cfg.TEST.NMS)
    boxes = boxes[keep]
    features = feat_dic[blob_name][inds][keep]
    if boxes.shape[0] == 0:
        return None, None
    features = features.reshape(features.shape[0], -1)
    return boxes, features
