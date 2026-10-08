#!/bin/bash

OPTIONS=$(getopt -o m:p:h --long model:,port:,help -- "$@")
if [ $? -ne 0 ]; then
    echo "Invalid arguments"
    exit 1
fi

eval set -- "$OPTIONS"

MODEL="google/gemma-3-270m-it"
# MODEL="meta-llama/Llama-3.2-1B"
# MODEL="unsloth/Llama-3.2-1B-Instruct"
# MODEL="google/gemma-3-1b-it"
# MODEL="HuggingFaceTB/SmolLM2-360M-Instruct"
# MODEL="meta-llama/Llama-3.2-1B"

PORT="8000"

while true; do
    case "$1" in
        -m | --model)
            MODEL="$2"
            shift 2
            ;;
        -p | --port)
            PORT="$2"
            shift 2
            ;;
        -h | --help)
            echo "Usage: $0 --model <model_name> --port <port_number>"
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unexpected option: $1"
            exit 1
            ;;
    esac
done

echo "Model: $MODEL"
echo "Port: $PORT"

vllm serve $MODEL --port $PORT --max_num_batched_tokens 2048 --max_num_seqs 32 --gpu_memory_utilization 0.7 --max_model_len 1024
##512 , 1536, 2048
# vllm serve $MODEL --port $PORT --max_num_batched_tokens 1024 --max_num_seqs 8 --gpu_memory_utilization 0.7 --max_model_len 1024 --chat-template ./benchmarks/llama-3.jinja

