import os
import uuid
import logging
from io import BytesIO

import numpy as np
from sqlalchemy import Column, String, Integer, \
    create_engine, ForeignKey, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from _init_env import OUTPUT_DIR
from _init_env import project_configuration

Base = declarative_base()
url = project_configuration.get('database', 'address')
engine = create_engine(url)
DBSession = sessionmaker(bind=engine)
session = DBSession()
logger = logging.getLogger(__name__)


# ORM definition
class Person(Base):
    # noinspection PyShadowingNames
    def __init__(self, person_identifier, person_feature):
        self.feature = adapt_ndarray(person_feature)
        self.identifier = person_identifier

    __tablename__ = "person"
    identifier = Column(String(256), primary_key=True)
    feature = Column(BLOB, nullable=False)

    def get_feature_array(self):
        return adapt_blob(self.feature)

    def to_dic(self):
        return {"identifier": self.identifier}


class Video(Base):
    __tablename__ = "video"
    identifier = Column(String(256), primary_key=True)
    step = Column(Integer, nullable=False)

    def to_dic(self):
        return {"identifier": self.identifier, "step": self.step}


class VideoFeature(Base):

    def __init__(self, frame_no, video_identifier, feature, boxes):
        self.frame_no = frame_no
        self.video_identifier = video_identifier
        self.feature = adapt_ndarray(feature)
        self.boxes = adapt_ndarray(boxes)

    __tablename__ = "video_feature"
    frame_no = Column(Integer, primary_key=True)
    video_identifier = Column(String(256), ForeignKey('video.identifier'), primary_key=True)
    feature = Column(BLOB, nullable=False)
    boxes = Column(BLOB, nullable=False)

    def get_feature_array(self):
        return adapt_blob(self.feature)


class Trace(Base):
    __tablename__ = "trace"
    trace_id = Column(Integer, primary_key=True)
    person_identifier = Column(String(256), ForeignKey('person.identifier'))
    video_identifier = Column(String(256), ForeignKey('video.identifier'))
    start_frame = Column(Integer, nullable=False)
    end_frame = Column(Integer, nullable=False)

    def to_dic(self):
        return {
            "trace_id": self.trace_id,
            "person_identifier": self.person_identifier,
            "video_identifier": self.video_identifier,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame
        }


compressor = 'zlib'


# noinspection PyTypeChecker
def adapt_ndarray(ndarray):
    out = BytesIO()
    np.save(out, ndarray)
    out.seek(0)
    return out.read().encode(compressor)


# noinspection PyTypeChecker
def adapt_blob(binary_text):
    out = BytesIO(binary_text)
    out.seek(0)
    out = BytesIO(out.read().decode(compressor))
    ndarray = np.load(out)
    return ndarray


# noinspection SqlNoDataSourceInspection
def delete_all():
    session.execute("delete from trace")
    session.execute("delete from video_feature")
    session.execute("delete from person")
    session.execute("delete from camera")
    session.commit()


def close():
    session.close()


def init_db():
    Base.metadata.create_all(engine)


def drop_db():
    Base.metadata.drop_all(engine)


def get_all(objs):
    return session.query(objs).all()


def link(kv):
    for k in kv:
        os.symlink(kv[k], os.path.join(OUTPUT_DIR, k))


# noinspection PyShadowingNames
def persist_process_task(task_descriptor, processed_task_data):
    delete_all()
    person = [Person(identifier, processed_task_data['processed_person'][identifier])
              for identifier in processed_task_data['processed_person']]
    processed_video = processed_task_data['processed_videos']
    videos = [Video(identifier=identifier, step=processed_task_data['step'])
              for identifier in processed_video]
    video_features = []
    for video_identifier in processed_video:
        sub_video = processed_video[video_identifier]
        for features, boxes, frame_no in zip(sub_video['features'], sub_video['boxes'], sub_video['frame_nos']):
            video_features.append(VideoFeature(frame_no, video_identifier, features, boxes))
    trace_map = processed_task_data['trace']
    trace = []
    for person_identifier in trace_map:
        for video_identifier in trace_map[person_identifier]:
            trace.extend([Trace(person_identifier=person_identifier,
                                video_identifier=video_identifier,
                                start_frame=start,
                                end_frame=end) for start, end in trace_map[person_identifier][video_identifier]])
    session.add_all(person)
    session.add_all(videos)
    session.commit()
    session.add_all(video_features)
    session.add_all(trace)
    session.commit()
    logger.info("Data stored to database")
    link(task_descriptor["videos"])
    link(task_descriptor["person"])
    logger.info("Link created")


# import os.path as osp
# __video_mat_path = osp.join(PERSON_SEARCH_HOME, "person_search", "output")
#
#
# def store_mat(data, identifier):
#     si.savemat(osp.join(__video_mat_path, str(identifier)), data, do_compression=True, appendmat=False)
#     return identifier
#
#
# def read_mat(identifier):
#     return si.loadmat(osp.join(__video_mat_path, str(identifier)), squeeze_me=True)

if __name__ == "__main__":
    # test
    drop_db()
    init_db()
    import scipy.io as si

    mat = si.loadmat("/home/sunha/Downloads/person_search/output/videoMat/test_50.mat")
    # person_image = cv2.imread("/home/sunha/Projects/person_search/person_search/input/query.png")
    person_identifier = str(uuid.uuid1()).replace("-", "")
    person = Person(person_identifier, mat['features'][0][2][0])
    video_identifier = identifier = str(uuid.uuid1()).replace("-", "")
    video = Video(identifier=video_identifier, step=50)
    feature = mat['features'][0][2]
    boxes = mat['boxes'][0][2]
    video_feature = VideoFeature(0, video_identifier, feature, boxes)
    session.add(person)
    session.add(video)
    session.add(video_feature)
    session.commit()

    person = session.query(Person).first().get_feature_array()
    feature = session.query(VideoFeature).first().get_feature_array()
    print("person_shape:%s,feature_shape:%s,dot:%s" % (person.shape, feature.shape, feature.dot(person)))
    session.close()
