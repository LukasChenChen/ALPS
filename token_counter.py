import tiktoken
import json

dataset_path = "system_prompts.json"
    # Push interactive prompts to the queue
with open(dataset_path) as f:
    dataset = json.load(f)

for i in range(len(dataset)):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    # encoding.encode("tiktoken is great!")
    # [83, 1134, 30001, 318, 1049, 0]
    num_tokens = len(encoding.encode(dataset[i]['system_prompt']))
    print("token_count of %s is %s "% (dataset[i]['app'], num_tokens))
# num_tokens = 6