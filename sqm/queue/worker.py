import requests
import uuid
from openai import OpenAI
from sqm.endpoints.endpoint import Endpoint
import logging

log = logging.getLogger(__name__)
# log.setLevel(logging.INFO)

INF = float("inf")
class Worker:
    """
    Worker class that represents a single instance of vLLM in the system.
    """

    def __init__(self, address, port, endpoint, model):
        """
        Initialize a worker instance. Uses openAI API to communicate with the worker.
        :param address: The address of the worker.
        :param port: The port of the worker.
        """
        self.address = f"http://localhost:{port}"
        self.endpoint = endpoint
        self.openai_api_base = f"{self.address}/v1"
        self.openai_api_key = "local"
        self.client = OpenAI(
            api_key=self.openai_api_key,
            base_url=self.openai_api_base,
        )
        self.worker_id = uuid.uuid4()
        self.model = model
        self.count = 0

        log.info(f"Worker {self.worker_id} registered at {self.address}")


    def add_request(self, prompt, model):
        """
        Add a request to the worker.
        :param prompt: The prompt to be added.
        :param model: The model to be used.
        """

        # if self.endpoint.model != model:
        #     self.endpoint.model_swap(model)
        log.info("worker add")

        try:
            completion = self.client.chat.completions.create(model=model, messages=prompt)
            self.count += 1
            print("reuqest count: %s" % self.count)

            log.info("Result of query: %s" % completion)
        except Exception as e:
            log.error(f"Error in adding request in worker: {e}")

    def _read_metrics(self, metric_name):
        """
        Reads all metrics from the worker and checks for a match with the metric name.
        """
        
        metrics = requests.get(f"{self.address}/metrics")


        for line in metrics.text.splitlines():
            if line.startswith(metric_name):
                return float(line.split()[-1])

    def get_backpressure(self):
        """
        Get the backpressure of the worker i.e. the number of requests currently being served.
        Includes running, queued and swapped requests.
        return: The backpressure of the worker.
        """

        try:
            running_requests = self._read_metrics("vllm:num_requests_running")
            queued_requests = self._read_metrics("vllm:num_requests_waiting")
            #deprecated
            # swapped_requests = self._read_metrics("vllm:num_requests_swapped")

            # backpressure = running_requests + queued_requests + swapped_requests

            backpressure = running_requests + queued_requests

            return backpressure
        except Exception as e:
            # If the worker is not reachable, return infinite backpressure
            # print("-----------backpressure problem!-------")
            return INF

    def __hash__(self):
        return hash(self.worker_id)

    def get_metrics(self):
        log.info("----get final metrics----")
        try: 
            latency = self._read_metrics("vllm:request_success_total")

            return latency
        except Exception as e:
            # If the worker is not reachable, return infinite backpressure
            return 0
