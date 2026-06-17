#!/bin/bash

# CONFIGURATION - set environment and directories

SPOC_ENV="ana01_spoc_venv"
SPOC_DIR="/mnt/scratch/SPOC"

# Input and output directories - edit paths as needed
AFM_INPUT_DIR="/mnt/storage/ana01/results/afm_14_TRA2A_RNase_gap_fill_copy"     #should be a COPY of original AF output parent dir - w/ removed failed models - due to file renaming in SPOC
SPOC_OUTPUT_DIR="/mnt/storage/ana01/results/SPOC_afm_14_TRA2A_RNase_gap_fill"

# Log files
MAIN_LOG_FILE="${SPOC_OUTPUT_DIR}/main.log"
LOGS_DIR="${SPOC_OUTPUT_DIR}/logs"


# SETUP - make output directory, source conda and activate spoc_venv
mkdir -p "$SPOC_OUTPUT_DIR" "$LOGS_DIR" 

source ~/miniconda3/etc/profile.d/conda.sh 
conda activate "$SPOC_ENV" || {
  echo "Error: could not activate environment $SPOC_ENV"
  exit 1
}


# Start the main log (overwrite if it exists)
echo "=== SPOC batch run started: $(date) ===" > "$MAIN_LOG_FILE"
echo "Input dir:  $AFM_INPUT_DIR" >> "$MAIN_LOG_FILE"
echo "Output dir: $SPOC_OUTPUT_DIR" >> "$MAIN_LOG_FILE"
echo >> "$MAIN_LOG_FILE"

# Track total runtime
batch_start_time=$(date +%s)


# MAIN LOOP 
# Iterate through each *multimer subdirectory in AFM_INPUT_DIR, and score the prediction with SPOC
for model_dir in "$AFM_INPUT_DIR"/*multimer; do       #take *multimer subdirs, ignore /logs and master.log
    if [ -d "$model_dir" ]; then                      #make sure it's a directory
        model_name=$(basename "$model_dir")
        
       # Log file for this model
        model_log="$LOGS_DIR/${model_name}.log"
        
        echo ">>> Running SPOC on $model_name ..."
        echo "[START] $(date): $model_name" >> "$MAIN_LOG_FILE"
        model_start_time=$(date +%s)

       # Run SPOC inside main output folder so all logs get named and stored in /logs and CSVs go into SPOC_outputs/
        (
          cd "$SPOC_OUTPUT_DIR" || exit
          python3 "$SPOC_DIR/run.py" "$model_dir" > "$model_log" 2>&1
        )
        exit_code=$?

        model_end_time=$(date +%s)
        runtime=$((model_end_time - model_start_time))
        runtime_min=$(echo "scale=2; $runtime/60" | bc)


        # Scan log for SPOC errors
        if [ $exit_code -ne 0 ] || grep -q "No complexes to analyze found" "$model_log"; then
            echo "[ERROR] $(date): $model_name encountered SPOC errors, see $model_log (runtime: ${runtime_min} min)" >> "$MAIN_LOG_FILE"
        else
            echo "[OK] $(date): $model_name finished successfully (runtime: ${runtime_min} min)" >> "$MAIN_LOG_FILE"
        fi

        echo ">>> Finished $model_name. Runtime: ${runtime_min} min. Logs: $model_log"
        echo
    fi
done

# Wrap up
batch_end_time=$(date +%s)
total_runtime=$((batch_end_time - batch_start_time))
total_runtime_hr=$(echo "scale=2; $total_runtime/3600" | bc)

echo >> "$MAIN_LOG_FILE"
echo "=== SPOC batch run completed: $(date) ===" >> "$MAIN_LOG_FILE"
echo "Total runtime: ${total_runtime_hr} hours" >> "$MAIN_LOG_FILE"


#Concatenate all individual model results into a single batch summary table in the parent SPOC output directory (spoc_summary.csv)
echo ">>> Building SPOC summary table..." >> "$MAIN_LOG_FILE"
python3 /mnt/users/ana01/AF-classifier/pipeline_scripts/03_SPOC_scripts/SPOC_summary.py "${SPOC_OUTPUT_DIR}"
echo ">>> Summary table complete." >> "$MAIN_LOG_FILE"

echo "All jobs completed successfully! :)"

