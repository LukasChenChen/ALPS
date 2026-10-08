from sqm.queue.group import Group
from sqm.queue.serve_queue import ServeQueue
from sqm.config import Config
from sqm.scheduler.wt_predictor import WTPredictor
from bidict import bidict
import time
from collections import deque
import logging

log = logging.getLogger(__name__)


class Scheduler:
    """
    Scheduler class is responsible for managing the scheduling of the queue.
    It is responsible for checking for SLO violations and reordering the queue based on the scheduling policy.
    """

    def __init__(self, policy="edf"):
        """
        Initializes the scheduler with a scheduling policy and a RWTEstimator object.
        :param policy: The scheduling policy for the scheduler.
        """
        self.policy = policy
        self.wt_predictor = WTPredictor()
        self.config = Config()

    def _update_all_slos(self, sqs):
        """
        Updates the SLOs for all requests in the virtual queues based on current time.
        :param sqs: The list of virtual queues.
        """
        for sq in sqs:
            for group in sq.groups:
                for request in group.requests:
                    curr_time = time.time()
                    request.slo -= curr_time - request.start_time
                    request.slo = (
                        request.slo
                        // self.config.slo_granularity
                        * self.config.slo_granularity
                    )
                    request.start_time = curr_time

    def check_violation(self, sqs):
        """
        Checks for SLO violations in the virtual queues.
        :param sqs: The list of virtual queues.
        :return: True if there is a violation, False otherwise.
        """
        self._update_all_slos(sqs)

        for sq in sqs:
            est_time = 0
            # curr_model = None

            for group in sq.groups:

                waiting_time = self.wt_predictor.get_waiting_time(group)

                est_time += waiting_time

                if est_time > group.slo:
                    return True

        return False

    def reorder(self, sqs):
        """
        Reorders the virtual queues based on the scheduling policy.
        :param sqs: The list of virtual queues.
        :return: The reordered list of virtual queues.
        """
        if self.policy == "edf":
            return self._reorder_edf(sqs)
        elif self.policy == "vllm":
            return sqs
        else:
            return self._reorder_edf(sqs)

    def _reorder_edf(self, sqs):
        """
        Reorders the virtual queues based on the Earliest Deadline First (EDF) policy.
        :param sqs: The list of virtual queues.
        :return: The reordered list of virtual queues.
        """
        for sq in sqs:
            groups = list(sq.groups)
            groups.sort(key=lambda x: x.slo)
            sq.groups = deque(groups)

        return sqs

   