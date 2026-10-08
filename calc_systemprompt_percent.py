import json
from datasets import load_dataset
import tiktoken
import numpy as np
# dataset_path = "system_prompts.json"
#     # Push interactive prompts to the queue
# with open(dataset_path) as f:
#     dataset = json.load(f)


# dataset = load_dataset("Naomibas/llm-system-prompts-benchmark", split = "train")

# dataset = load_dataset("QuixiAI/SystemChat-2.0", , split = "train")

filename = "QuixiAI/SystemChat-2.0"
data = []
if filename == "Naomibas/llm-system-prompts-benchmark":
    dataset = load_dataset("Naomibas/llm-system-prompts-benchmark", split = "train")
    for i in range(len(dataset)):
        encoding = tiktoken.encoding_for_model("gpt-4o")
        
        num_sys_tokens = len(encoding.encode(dataset[i]['prompt']))
        num_user_tokens = len(encoding.encode(dataset[i]['probe']))
    
        print(num_sys_tokens/(num_sys_tokens+num_user_tokens)*100)

elif filename == "QuixiAI/SystemChat-2.0":

    dataset = load_dataset("QuixiAI/SystemChat-2.0",  split = "train")
    # dataset = dataset['messages'][:100]
    dataset = dataset['messages']
    # dataset = dataset[:100]
    print("dataset len %s " % len(dataset))
    print("dataset first item len %s " % len(dataset[0]))
    print("dataset first item first entry len %s " % len(dataset[0][0]))
    for i in range(len(dataset)):
        encoding = tiktoken.encoding_for_model("gpt-4o")
        
        num_sys_tokens = len(encoding.encode(dataset[i][0]['content']))
        num_user_tokens = len(encoding.encode(dataset[i][1]['content']))

        # print(num_sys_tokens/(num_sys_tokens+num_user_tokens)*100)
        data.append(num_sys_tokens/num_user_tokens)

import csv

with open("prompt_percentage.csv", 'w') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(data)       


import matplotlib.pyplot as plt
import scipy.stats as st
# import numpy as np
plt.axvline(x=0.5, color='r', linestyle='--', linewidth=1)

plt.axvline(x=1, color='r', linestyle='--', linewidth=1)
plt.xlim(0, 5)
# data = np.random.normal(1.0, 1.0, size=200)

plt.rcParams['axes.labelsize'] = 25
plt.ecdf(data, linewidth=2)

extraticks = [0.5]
plt.xticks(list(plt.xticks()[0]) + extraticks)

# plt.hist(data, density=False, bins=100)
plt.xlabel("Ratio of tokens in system and user prompts")
plt.ylabel("CDF")
plt.grid()
# mn, mx = plt.xlim()
# plt.xlim(mn, mx)
# kde_xs = np.linspace(mn, mx, 300)
# kde = st.gaussian_kde(data)
# plt.plot(kde_xs, kde.pdf(kde_xs), label="PDF")
# plt.legend(loc="upper left")
plt.title("CDF of ratio between system and user tokens")

# plt.savefig('pdf.png')
# Save the plot as a PDF  
plt.savefig("cdf.pdf", format="pdf")  
