import uuid
from collections import deque
from sqm.queue.request import Request
from bidict import bidict


class ServeQueue:
    """
    A ServeQueue is a queue that contains a list of request groups. Each request group is a list of requests.
    """

    def __init__(self):
        self.sq_id = uuid.uuid4()
        self.groups = deque()

    def add_group(self, group):
        self.groups.append(group)

    def pop_group(self):
        return self.groups.popleft()

    def get_head_group(self):
        return self.groups[0]

    def __hash__(self):
        return hash(self.sq_id)
