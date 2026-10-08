from sqm.queue.queue import Queue
from sqm.endpoints.endpoint import Endpoint
import asyncio
import time
import json
import logging
from sqm.scheduler.app_indicator import AppIndicator 

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("experiment.log", "w"),
        logging.StreamHandler()
    ],
)

logging.getLogger("urllib3").setLevel(logging.WARNING)

async def basic_test():
    # Test description
    log.info("Basic test for Alps")
    # model_name = "google/gemma-3-1b-it"
    model_name = "google/gemma-3-270m-it"

    # model_name="meta-llama/Llama-3.2-1B"
    # model_name="HuggingFaceTB/SmolLM2-360M-Instruct"


    # Start vLLM endpoint
    endpoint = Endpoint(address="localhost", port=8000, model=model_name)

    time.sleep(10)
    start_time = time.time()

    # Create a Queue object
    q = Queue() 

    # Intialize workers
    q.register_worker("localhost", 8000, endpoint, model_name)

    # Run the queue
    queue_run_task = asyncio.create_task(q.run_queue())
    
    # Create sample prompts for the queue
    prompts = ["Whats the captial of France?",
               "Name the eight planets in the solar system."]           
    
    app_indicator = AppIndicator()

    log.info('create prompts')
    dataset_path = "mixed_data.json"
    # Push interactive prompts to the queue
    with open(dataset_path) as f:
        dataset = json.load(f)
        
    request_num = 200
    for i in range(min(request_num, len(dataset))):
        log.info('get in the loop dataset')
        q.push(user_prompt=dataset[i]['instruction'], model=model_name, start_time = time.time(), slo=10, sys_prompt = dataset[i]['sys_prompt'], est_token_number=dataset[i]['pred'], app_indicator = app_indicator)
        log.info('app_indicator length: %s' % len(app_indicator.sys_prompts))

    log.info("successful request counter is : %s" % q.workers[0].get_metrics())

    end_time = time.time()
    seconds_elapsed = end_time - start_time

    with open("timefile.txt", "w") as f:
        f.write("ALPS time: %s" % seconds_elapsed)


    
if __name__ == "__main__":
    asyncio.run(basic_test())
