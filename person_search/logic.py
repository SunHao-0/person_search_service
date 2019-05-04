from persistence import Camera, Person, Trace, create, create_all, delete_all
import process
import random
import string


def search(video_name, person_images):
    delete_all()
    # process video ,store mate data to db
    random_str = lambda: ''.join(random.sample(string.ascii_letters + string.digits, 8))
    video_identifier, step, processed_data, person_uuids = process.process_video(video_name, person_images)
    random_name = [random_str() for _ in person_uuids]
    person = [Person(identifier=person_uuid, name=r_name)
              for person_uuid, r_name in zip(person_uuids, random_name)]
    create_all(person)
    create(Camera(identifier=video_identifier, step=step, name=random_str()))
    traces = process.generate_trace(processed_data, step)
    traces_persist(traces, video_identifier)


def traces_persist(traces, video_identifier):
    print(traces)
    for (person_identifier, trace) in traces:
        person_traces = [Trace(person_identifier=person_identifier,
                               camera_identifier=video_identifier,
                               start_frame=int(start),
                               end_frame=int(end)) for start, end in trace]
        create_all(person_traces)
