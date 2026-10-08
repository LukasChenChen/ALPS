import uuid
from collections import deque


class Group:
    """
    Group class is used to store the requests that are in the same request group.
    Request group is a group of requests that have the same model and similar clustered SLO.
    """

    def __init__(self, app, slo, model):
        self.group_id = uuid.uuid4()
        # self.model = model
        self.app = app
        self.slo = slo
        self.requests = deque()
        self.model = model

    def add_request(self, request):
        self.requests.append(request)

    def pop_request(self):
        
        return self.requests.popleft()

    def __hash__(self):
        return hash(self.group_id)
