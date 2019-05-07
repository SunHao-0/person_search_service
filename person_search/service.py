from flask import Flask, jsonify, abort, request
from persistence import Person, Trace, get_all, session, Video
from _init_env import project_configuration
import redis

app = Flask(__name__)

__Host = project_configuration.get("subscriber", "address")
__redis_channel = project_configuration.get("subscriber", "channel")
__redis_connection = redis.Redis(host=__Host)


@app.route('/')
def index():
    return "useless"


@app.route('/person_search/api/task', methods=['POST'])
def submit_task():
    if not request.json or 'video_paths' not in request.json \
            or 'person_image_paths' not in request.json:
        abort(400)
    msg = request.json
    __redis_connection.publish(__redis_channel, jsonify(msg))


@app.route('/person_search/api/person')
def get_person():
    all_person = get_all(Person)
    return jsonify([person.to_dic() for person in all_person])


@app.route('/person_search/api/person/<string:person_identifier>')
def get_one_person(person_identifier):
    target_person = session.query(Person).filter(Person.identifier == person_identifier).one()
    if target_person is None:
        abort(404)
    return jsonify(target_person.to_dic())


@app.route('/person_search/api/cameras')
def get_all_camera():
    return jsonify([camera.to_dic() for camera in get_all(Video)])


@app.route('/person_search/api/traces')
def get_all_trace():
    all_person_trace = get_all(Trace)
    person_dic = {trace.person_identifier: [] for trace in all_person_trace}
    for trace in all_person_trace:
        person_dic[trace.person_identifier] \
            .append((trace.video_identifier, 1, trace.start_frame, trace.end_frame))
    for person_identifier in person_dic:
        person_dic[person_identifier].sort(key=lambda x: x[2])
    return jsonify(person_dic)


@app.route('/person_search/api/traces/<string:person_identifier>/<string:video_identifier>')
def get_specific_trace(person_identifier, video_identifier):
    traces = session.query(Trace).filter(Trace.person_identifier == person_identifier
                                         and Trace.video_identifier == video_identifier).all()
    return jsonify([trace.to_dic() for trace in traces])


@app.route('/person_search/api/traces/<string:person_identifier>')
def get_person_trace(person_identifier):
    traces = session.query(Trace).filter(Trace.person_identifier == person_identifier).all()
    return jsonify([trace.to_dic() for trace in traces])


def start():
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
