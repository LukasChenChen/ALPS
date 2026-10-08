import asyncio
from collections import deque
from sqm.config import Config
from sqm.queue.serve_queue_manager import ServeQueueManager
from sqm.queue.worker import Worker
from sqm.queue.request import Request
from sqm.endpoints.endpoint import Endpoint
import logging


log = logging.getLogger(__name__)


class Queue:
    """
    Queue class is responsible for managing the queue of requests and workers.
    It is responsible for pushing requests to the queue and running the queue.
    """

    def __init__(self):
        """
        Initializes the queue with an empty list of workers, a Config object and a ServeQueueManager object.
        """
        self.workers = []
        self.config = Config()
        self.sq_manager = ServeQueueManager()

    def register_worker(self, address, port, endpoint, model):
        """
        Registers a worker with the queue.
        A worker is an LLM instance in the system.
        :param address: The address of the worker.
        :param port: The port of the worker.
        """
        worker = Worker(address, port, endpoint, model)
        self.workers.append(worker)
        self.sq_manager.add_worker(worker)

        

    def push(self, user_prompt, model, slo, start_time, sys_prompt, est_token_number, app_indicator):
        """
        Pushes a request to the serve queue manager.
        :param prompt: The prompt for the request.
        :param model: The model for the request.
        :param slo: The SLO for the request.
        :param start_time: The time at which the request was inserted into the queue. Insertion time is only used for SLO calculation and can be updated during request lifetime.
        """
        log.info("queue push request")

        new_request = Request(
            user_prompt= user_prompt, model=model, slo=slo, start_time=start_time, sys_prompt = sys_prompt, est_token_number = est_token_number
        )
        
        log.info("finish creating  request")
        new_request.append_system_prompt()

        ##do the hash and indicate the app
        app = app_indicator.get_app(new_request)

        log.info("app is %s " % app)

        new_request.app = app


        log.info("sq_manager add request")

        self.sq_manager.add_request(new_request)

    async def run_queue(self):
        """
        Runs the queue. The queue runs in an infinite loop and continuously interacts with the serve queue engine.
        If a request is found, the queue checks for backpressure and if the worker can handle the request.
        If the worker can handle the request, the request is popped from the serve queue engine and added to the worker.
        """

        while True:
            self.sq_manager.reorder_sqs()
            for worker in self.workers:
                try:
                    backpressure = worker.get_backpressure()
                    has_request = self.sq_manager.has_request(worker)

                    if has_request and backpressure < self.config.max_batch_size:
                        request_to_serve = self.sq_manager.pop_request(worker)
                        log.info("handling request: %s" % request_to_serve.request_id)
                        await asyncio.to_thread(
                            worker.add_request,
                            request_to_serve.prompt,
                            request_to_serve.model,
                        )
                except asyncio.CancelledError as e:
                    log.error("handling cancelled error", e)

    async def run_queue_vllm(self):
        """
        Runs the queue for vllm, which means no reorder or group. The queue runs in an infinite loop and continuously interacts with the serve queue engine.
        If a request is found, the queue checks for backpressure and if the worker can handle the request.
        If the worker can handle the request, the request is popped from the serve queue engine and added to the worker.
        """

        while True:
            for worker in self.workers:
                try:
                    backpressure = worker.get_backpressure()
                    has_request = self.sq_manager.has_request(worker)

                    if has_request and backpressure < self.config.max_batch_size:
                        request_to_serve = self.sq_manager.pop_request(worker)
                        log.info("handling request: %s" % request_to_serve.request_id)
                        await asyncio.to_thread(
                            worker.add_request,
                            request_to_serve.prompt,
                            request_to_serve.model,
                        )
                except asyncio.CancelledError as e:
                    log.error("handling cancelled error", e)
