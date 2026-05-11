#!/bin/bash
#SBATCH --partition=mit_normal
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --time=12:00:00
#SBATCH --job-name=MethodClassify
#SBATCH --output=logs/%x_%j.out
#SBATCH --error=logs/%x_%j.err

cd /home/jinzhta/RevGPT_dev/superconductivity
nice -n 19 /home/jinzhta/.conda/envs/ml-research/bin/python 5_7_LLM_method_classify_parallel.py
