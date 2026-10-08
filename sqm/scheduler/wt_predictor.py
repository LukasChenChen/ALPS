from sqm.queue.group import Group
from sqm.config import Config


class WTPredictor:

    def __init__(self):
        self.config = Config()
        self.pred_step = 50

    def get_waiting_time(self, group):

        num_requests = len(group.requests)
        # est_workload_tokens = self.config.workload_tokens
        est_token_throughput = self.config.token_throughput[group.model]

        # return num_requests * est_workload_tokens / est_token_throughput
        est_token_number = 0
        for request in group.requests:
            est_token_number += self.get_est_token_num(request) * self.pred_step
       
        return num_requests * est_token_number / est_token_throughput

    ## need to use the pretrained model
    def get_est_token_num(self, request):
       
        return request.est_token_number
