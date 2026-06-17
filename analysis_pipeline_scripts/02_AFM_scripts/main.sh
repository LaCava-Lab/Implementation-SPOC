#!/bin/bash
#NOTE: 3 paths to edit 

FASTA_FOLDER="/mnt/storage/ana01/results/fasta_file_TRA2A_ORF2"
MAIN_LOG_FILE="/mnt/storage/ana01/results/afm_14_TRA2A_RNase_gap_fill/master.log"

# Redirect stdout and stderr to the main log file (overwrite existing file)
exec >> "$MAIN_LOG_FILE" 2>&1

echo "Starting!"
echo "Date: $(date)"

# Define the maximum number of concurrent jobs
MAX_JOBS=1

# Function to wait for running jobs to drop below the limit
wait_for_slot() {
  while (( $(tmux list-sessions 2>/dev/null | grep -c "alphafold_") >= MAX_JOBS )); do
    echo "Waiting for an available slot..."
    sleep 5  # Check every 5 seconds
  done
}

# Loop through each fasta file and run AlphaFold jobs
for fasta_file in "$FASTA_FOLDER"/*.fasta; do
  echo "Processing file: $fasta_file"
  fasta_basename=$(basename "$fasta_file" .fasta)
  ALPHAFOLD_LOG_FILE="/mnt/storage/ana01/results/afm_14_TRA2A_RNase_gap_fill/logs/${fasta_basename}_alphafold.log"

  # Wait for a slot if the number of running jobs has reached the limit
  wait_for_slot

  # Start the AlphaFold job in a new tmux session
  ./run_tmux.sh "$fasta_file" "$ALPHAFOLD_LOG_FILE"
done

# Wait for all remaining jobs to complete
while (( $(tmux list-sessions 2>/dev/null | grep -c "alphafold_") > 0 )); do
  echo "Waiting for all jobs to finish..."
  sleep 5
done

echo "All jobs completed!"



