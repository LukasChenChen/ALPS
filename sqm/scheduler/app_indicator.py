from sqm.config import Config
import logging


log = logging.getLogger(__name__)

class AppIndicator:
    """
    AppIndicator class is responsible for indicating the app from the system prompt.
    It converts system prompt to app.
    """

    def __init__(self):
        self.config = Config()
        ##need a map for <system_prompt_hash, app_id>
        self.sys_prompts = []
    
    "should indicate app from system prompt"
    "the app is the index of the hash value in the system_prompts"
    def get_app(self, request):
        log.info("start to get_app")
        hash_value = self.__hash__(request.sys_prompt)
        log.info("hash_value %s " % hash_value)
        ## find it from list
        if self.sys_prompts:
            for i in range(len(self.sys_prompts)):
                if hash_value == self.sys_prompts[i]:
                    return i
        ##can't find it, then add
        self.sys_prompts.append(hash_value)
        log.info("append hash value")
        return len(self.sys_prompts) - 1

    

    def __hash__(self, sys_prompt):
      log.info("start to hash")
      return hash(sys_prompt)


