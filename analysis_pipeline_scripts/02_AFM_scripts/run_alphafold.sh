#!/bin/bash
#NOTE TO SELF: 1 path to edit

# Set paths
OUTPUT_DIR="/mnt/storage/ana01/results/afm_14_TRA2A_RNase_gap_fill"


# Arguments
FASTA_FILE=$1
ALPHAFOLD_LOG_FILE=$2

# Redirect stdout and stderr to the specified log file (overwrite existing file)
exec >> "$ALPHAFOLD_LOG_FILE" 2>&1

# Log the current PID at the beginning of the log file
echo "PID: $$"
echo "Date: $(date)"
echo "Processing file: $FASTA_FILE"

# Run AlphaFold default 5 models for multimer prediction, constant seed = 1, only 1 seed per model, no relaxation
python3 /mnt/scratch/alphafold/docker/run_docker_random_seed.py \
    --fasta_paths="$FASTA_FILE" \
    --max_template_date=2022-01-01 \
    --gpu_devices=1 \
    --model_preset=multimer \
    --data_dir=/mnt/scratch/alphafold_ref \
    --models_to_relax=none \
    --num_multimer_predictions_per_model=1 \
    --random_seed=1 \
    --output_dir="$OUTPUT_DIR"

