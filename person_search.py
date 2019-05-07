import person_search.task_listener
import person_search.service
import os

if __name__ == "__main__":
    pid = os.fork()
    if pid == 0:
        person_search.task_listener.start()
    else:
        person_search.service.start()
