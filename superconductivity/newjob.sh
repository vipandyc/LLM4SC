#!/bin/bash
#SBATCH --account=vipandyc
#SBATCH --job-name=RevGPT
#SBATCH --gres=gpu:1
#SBATCH --time=2-00:00
#SBATCH --output="%x_%j.out"

nice -n 19 python 5_LLM_opinions_parallel.py
