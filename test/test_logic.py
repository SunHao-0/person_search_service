# encoding: utf-8
import _init_test_env
from person_search.process import process_video, generate_trace
import unittest
import scipy.io as si


class TestProcessLogic(unittest.TestCase):

    def test_process_video(self):
        input_path = "/home/sunha/Projects/person_search/person_search/input"
        video_path = input_path + "/test"
        person_path = input_path + "/query.png"
        process_video(video_path, [person_path])

    # def test_trace(self):
    #     data = si.loadmat("/home/sunha/Downloads"
    #                       "/person_search/track/output/video_mat/"
    #                       "c6bd54ee-6d85-11e9-815a-a402b9c89e2f.mat")
    #     trace = generate_trace(data)
    #     print(trace)
