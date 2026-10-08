from bidict import bidict
import uuid
from sqm.queue.serve_queue import ServeQueue
from sqm.queue.group import Group
from sqm.queue.request import Request
from sqm.scheduler.scheduler import Scheduler
import random
import logging

log = logging.getLogger(__name__)


class ServeQueueManager:
    """
    ServeQueueManager is the main class that manages the serve queues and groups.
    """

    def __init__(self):
        """
        Initializes the ServeQueueManager with empty serve queues, request to group mapping, group to serve queue
        mapping, serve queue to worker mapping, application to group mapping and a scheduler.
        """
        self.sqs = []
        self.request_to_group = {}
        self.group_to_sq = {}
        self.sq_worker_bimap = bidict({})
        self.app_group_bimap = bidict({})
        self.model_worker_bimap = bidict({})
        self.scheduler = Scheduler()

    def add_worker(self, worker):
        """
        Adds a worker to the serve queue engine. Creates a new serve queue associated with the worker.
        :param worker: Worker object
        """
        new_sq = ServeQueue()
        self.sqs.append(new_sq)
        self.sq_worker_bimap[new_sq] = worker
        log.info("sq_worker_bimap size: %s" % len(self.sq_worker_bimap))
        

    def add_request(self, request):
        """
        Adds a request to the serve queue engine. If a group with the same model and slo exists, adds the request to
        the group. Otherwise, creates a new group and adds the request to the new group.
        :param request: Request object
        """
        log.info('-----sq manager add_request----')
        if request.app in self.app_group_bimap:
            log.info("add to existing group, request id %s" % request.request_id)
            existing_group = self.app_group_bimap[request.app]
            existing_group.add_request(request)
            self.request_to_group[request] = existing_group
        else:
           
            new_group = Group(request.app, request.slo, request.model)
            new_group.add_request(request)

            self.app_group_bimap[request.app] = new_group
            self.request_to_group[request] = new_group
            # Select a random virtual queue to add the group to
            # sq_idx = random.choice(range(len(self.vqs)))
            # self.vqs[vq_idx].add_group(new_group)
            log.info("Adding new group with app %s" % request.app)
            #select a specific queue for the model
            for sq, worker in self.sq_worker_bimap.items():
                log.info("worker model is: %s" % worker.model)
                if worker.model == request.model:
                    log.info("worker model found with sq id %s" % sq.sq_id)
                    #which server q is
                    sq.add_group(new_group)

                    for index in range(len(self.sqs)):
                        if self.sqs[index].sq_id == sq.sq_id:
                            self.sqs[index] = sq
                            ## add the sq to the sqs
                            log.info("sqs index %s updated: " % index)
                            log.info("add to new group, request id %s" % request.request_id)
                            break
                else:
                    log.warning("cannot find corresponding instance in the worker")



    def pop_request(self, worker):
        """
        Pops a request from the virtual queue associated with the worker. If the group is empty, pops the group from the
        virtual queue.
        :param worker: Worker object
        :return: Request object
        """
        sq = self.sq_worker_bimap.inv[worker]
        group = sq.get_head_group()
        request = group.pop_request()

        if len(group.requests) == 0:
            sq.pop_group()

        return request

    def has_request(self, worker):
        """
        Checks if the serve queue associated with the worker has any requests.
        :param worker: Worker object
        :return: Boolean
        """
        sq = self.sq_worker_bimap.inv[worker]
        return len(sq.groups) > 0

    def reorder_sqs(self):
        """
        Reorders the serve queues based on the scheduler. If the scheduler detects an SLO violation, reorders the virtual
        queues. Else, keeps the queues as is.
        """
        if self.scheduler.check_violation(self.sqs):
            self.sqs = self.scheduler.reorder(self.sqs)
    
    # def add_request_simple(self, request):
    #     """
    #     add requests without grouping
    #     """

    #     if len(self.app_group_bimap) == 0:
    #         new_group = Group(request.app, request.slo, request.model)
    #         new_group.add_request(request)

    #         self.app_group_bimap[request.app] = new_group
    #         self.request_to_group[request] = new_group
    #     else:
    #         ##add to the current group
