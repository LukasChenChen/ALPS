from sqm.queue.queue import Queue
from sqm.endpoints.endpoint import Endpoint
import asyncio
import time
import json
import logging
from sqm.scheduler.app_indicator import AppIndicator 

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("experiment.log", "w"),
        logging.StreamHandler()
    ],
)

logging.getLogger("urllib3").setLevel(logging.WARNING)

async def basic_test():
    # Test description
    log.info("Basic test for vllm")

    model_name = "google/gemma-3-270m-it"
    # model_name="meta-llama/Llama-3.2-1B"
    model_name="HuggingFaceTB/SmolLM2-360M-Instruct"

    # Start vLLM endpoint
    endpoint = Endpoint(address="localhost", port=8000, model=model_name)

    time.sleep(10)

    # Create a Queue object
    q = Queue() 

    # Intialize workers
    q.register_worker("localhost", 8000, endpoint, model_name)

    q.sq_manager.scheduler.policy = "vllm"

    # # Run the queue
    # queue_run_task = asyncio.create_task(q.run_queue())  

    log.info('create prompts')
    dataset_path = "mixed_data.json"
    # Push interactive prompts to the queue
    with open(dataset_path) as f:
        dataset = json.load(f)
    INF = float("inf")
    ##wait for server to start up
    while True:
        try:
            backpressure = q.workers[0].get_backpressure()
            if backpressure == INF :
                time.sleep(10)
            else:
                log.warning("no backpressure")
                break
        except asyncio.CancelledError as e:
            time.sleep(10)
            log.error("handling cancelled error", e)
    
    log.info('start to run prompts')
    request_num = 200
    for i in range(min(request_num, len(dataset))):
        log.info('get in the loop dataset')
    
        messages=[
            {"role": "system", "content": dataset[i]['sys_prompt']},
            {"role": "user", "content": dataset[i]['instruction']}
        ]

        try:
            completion = q.workers[0].client.chat.completions.create(model=model_name, messages=messages)
            
            
            log.info("Result of query: %s" % completion)
        except Exception as e:
            log.error(f"Error in adding request in worker: {e}")


    # request_generator("./data/mixed_data.json", 2 , app_indicator)
    log.info("successful request counter is : %s" % q.workers[0].get_metrics())

async def send_request(model_name, message):
    """
    Runs the queue. The queue runs in an infinite loop and continuously interacts with the serve queue engine.
    If a request is found, the queue checks for backpressure and if the worker can handle the request.
    If the worker can handle the request, the request is popped from the serve queue engine and added to the worker.
    """

    try:
        completion = q.workers[0].client.chat.completions.create(model=model_name, messages=messages)
        

        log.info("Result of query: %s" % completion)
    except Exception as e:
        log.error(f"Error in adding request in worker: {e}")


    
if __name__ == "__main__":
    asyncio.run(basic_test())
