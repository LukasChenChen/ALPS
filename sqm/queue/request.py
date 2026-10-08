import uuid
import logging

log = logging.getLogger(__name__)


class Request:
    """
    Request class to store the request to LLM
    """

    def __init__(self, user_prompt, model, slo, start_time, sys_prompt, est_token_number):
        """
        :param prompt: The prompt to be sent to the model
        :param model: The model to be used for the request
        :param slo: The SLO for the request
        :param start_time: The time at which the request was inserted into the system
        """
        self.request_id = uuid.uuid4()
        self.user_prompt = user_prompt
        # Default SLO is 10 seconds
        self.model = model
        self.slo = slo
        ##why i cannot call it application?
        self.start_time = start_time
        self.sys_prompt = sys_prompt
        self.app = -1
        self.prompt = []
        self.est_token_number = est_token_number

    def append_system_prompt(self):
        """
        :param system_promt: the system prompt 
        :param user_prompt: the user prompt
        :return an array object to be used by chat.completions
        """
        ##append system prompt to prompt
        ##check open client completions create
        ## check vllm instruct template first
#         completion = client.chat.completions.create(
#   model="gpt-5",
#   messages=[
#     {"role": "developer", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Hello!"}
#   ]
# )
        messages=[
            {"role": "system", "content": self.sys_prompt},
            {"role": "user", "content": self.user_prompt}
        ]
       
        self.prompt = messages
        log.info("append system prompt: %s" % self.prompt)
        

    def __hash__(self):
        return hash(self.request_id)
