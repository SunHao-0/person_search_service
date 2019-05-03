"""Set up env for project, this script show be execute at start point of project"""
import os
import os.path as osp
import sys
import logging.config
from configparser import ConfigParser


def add_path(path):
    if path not in sys.path:
        sys.path.insert(0, path)


PERSON_SEARCH_HOME = os.environ.get("PERSON_SEARCH_HOME")
if PERSON_SEARCH_HOME is None:
    raise RuntimeError("PERSON_SEARCH_HOME env var is required")

project_configuration = ConfigParser()
config_file_path = osp.join(PERSON_SEARCH_HOME, "person_search", "app.conf")
project_configuration.read(config_file_path)
# Add caffe to PYTHONPATH
caffe_path = project_configuration.get("dependencies", "py_caffe_path")
add_path(caffe_path)
# Add lib to PYTHONPATH
lib_path = project_configuration.get("dependencies", "faster_rcnn_path")
add_path(lib_path)
# set up logger
logging_config_path = osp.join(PERSON_SEARCH_HOME, "person_search", "logger.conf")
logging.config.fileConfig(logging_config_path)
logger = logging.getLogger(__name__)
# disable logging from caffe
os.environ['GLOG_minloglevel'] = '2'
logger.info("\nCaffe path:%s\nLib path:%s\nProject config path:%s" % (caffe_path, lib_path, config_file_path))
