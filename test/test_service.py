import redis
import json

Host = "127.0.0.1"
channel = "video_process"
connection = redis.Redis(host=Host)

task = {
    "video_name": "test",
    "person_images_name": ["query.png", "test2.png", "test12.png"]
}
msg = json.dumps(task)
print("msg:%s" % msg)
connection.publish(channel, msg)
