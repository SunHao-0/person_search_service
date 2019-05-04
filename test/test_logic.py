# encoding: utf-8
import _init_test_env
from person_search.process import process_video, generate_trace, read_mat
from person_search.logic import traces_persist
from person_search.logic import search
import unittest
import scipy.io as si


class TestProcessLogic(unittest.TestCase):

    def test_process_video(self):
        input_path = "/home/sunha/Projects/person_search/person_search/input"
        video_path = input_path + "/test"
        person_path = input_path + "/query.png"
        process_video(video_path, [person_path])

    def test_trace(self):
        data = read_mat("3de34f926e4911e9ba78a402b9c89e2f")
        trace = generate_trace(data, 100)
        print(trace)

    def test_search(self):
        import os.path as osp
        input_path = "/home/sunha/Projects/person_search/person_search/input"
        video_path = input_path + "/test"
        person_path = ["query.png", "test2.png", "test12.png"]
        person_path = [osp.join(input_path, image_name) for image_name in person_path]
        search(video_path, person_path)

    def test_traces_persist(self):
        vid = "3de34f926e4911e9ba78a402b9c89e2f"
        data = read_mat(vid)
        traces = generate_trace(data, 100)
        traces_persist(traces, vid)
