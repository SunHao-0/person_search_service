import json
import logging

import redis

from _init_env import project_configuration
from logic import search

__logger = logging.getLogger(__name__)


def __get_subscribe():
    address = project_configuration.get("subscriber", "address")
    channel = project_configuration.get("subscriber", "channel")
    connection = redis.Redis(host=address)
    process_subscriber = connection.pubsub()
    process_subscriber.subscribe(channel)
    __logger.info("Process_subscriber listen on [Host:%s,Channel:%s]" % (address, channel))
    process_subscriber.listen()
    return process_subscriber


def start():
    process_subscriber = __get_subscribe()
    while True:
        msg = process_subscriber.parse_response(block=True)
        try:
            task = json.loads(msg[len(msg) - 1])
            if "video_paths" not in task or "person_image_paths" not in task \
                    or "step" not in task:
                raise RuntimeError("Bad message")
            search(task["video_paths"], task["person_image_paths"], task["step"])
        except Exception, e:
            __logger.warning("Error in processing msg:%s" % (str(msg)))
            print(e)


if __name__ == "__main__":
    start()
