#!/bin/bash

WORKINGDIR="DEFINE_PATH"
INPUT="$WORKINGDIR/FASTA_Temp"
OUTPUT="$WORKINGDIR/OUTPUT"
LOGFILE="$WORKINGDIR/job_status.log"

ALPHAFOLD_MSA_SCRIPT="DEFINE_PATH/design_tools/run_alphafold-msa_2.3.1.py"
ALPHAFOLD_GPU_SCRIPT="DEFINE_PATH/design_tools/run_alphafold-gpu_2.3.2.py"

mkdir -p "$INPUT"
mkdir -p "$OUTPUT"

echo "Job Status Log" > "$LOGFILE"
echo "=================" >> "$LOGFILE"

for file in "$INPUT"/*.fa; do
    JOB_NAME=$(basename "$file" .fa)
    JOB_OUTPUT="$OUTPUT/$JOB_NAME"
    LOGDIR="$WORKINGDIR/logs/$JOB_NAME"
    mkdir -p "$JOB_OUTPUT"
    mkdir -p "$LOGDIR"

    echo "Processing $file" | tee -a "$LOGFILE"

    if [ -f "$JOB_OUTPUT/features.pkl" ]; then
        echo "features.pkl found for $JOB_NAME. Skipping MSA generation." | tee -a "$LOGFILE"
    else
        echo "Running MSA for $file" | tee -a "$LOGFILE"
        
        start_time=$(date +%s)
        vmstat 1 | awk '{now=strftime("%Y-%m-%d %H:%M:%S "); print now $0}' > "$LOGDIR/${JOB_NAME}_cpu_usage.log" &
        vmstat_pid=$!
        
        python3 "$ALPHAFOLD_MSA_SCRIPT" \
            --fasta_paths="$file" \
            --output_dir="$JOB_OUTPUT" \
            --max_template_date=2040-01-01 \
            --db_preset=full_dbs \
            --model_preset=multimer \
            --use_precomputed_msas=True \
            2>&1 | tee "$LOGDIR/${JOB_NAME}_cpu.log"
        
        kill $vmstat_pid
        end_time=$(date +%s)
        echo "Total CPU execution time: $((end_time - start_time)) seconds" >> "$LOGDIR/${JOB_NAME}_cpu_time.log"
    fi

    echo "Running GPU prediction for $file" | tee -a "$LOGFILE"

    start_time=$(date +%s)
    vmstat 1 | awk '{now=strftime("%Y-%m-%d %H:%M:%S "); print now $0}' > "$LOGDIR/${JOB_NAME}_gpu_cpu_usage.log" &
    vmstat_pid=$!

    nvidia-smi --query-gpu=timestamp,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -l 1 > "$LOGDIR/${JOB_NAME}_gpu_usage.log" &
    nvidia_smi_pid=$!

    python3 "$ALPHAFOLD_GPU_SCRIPT" \
        --fasta_paths="$file" \
        --output_dir="$OUTPUT" \
        --data_dir="/mnt/ceph/alphafold_databases" \
        --mount_data_dir="/mnt/ceph/alphafold_databases" \
        --singularity_image_path="/home/vmathew/Desktop/temp/alphafold_2.3.2-1_sandbox" \
        --max_template_date=2040-01-01 \
        --db_preset=full_dbs \
        --model_preset=multimer \
        --num_multimer_predictions_per_model=1 \
        --use_gpu_relax=true \
        --models_to_relax=all \
        --benchmark=false \
        --use_precomputed_msas=true \
        --gpu_devices=0 \
        2>&1 | tee "$LOGDIR/${JOB_NAME}_gpu.log"

    kill $vmstat_pid
    kill $nvidia_smi_pid
    end_time=$(date +%s)
    echo "Total GPU execution time: $((end_time - start_time)) seconds" >> "$LOGDIR/${JOB_NAME}_gpu_time.log"

    echo "Completed processing $file" | tee -a "$LOGFILE"
done

echo "All jobs completed" | tee -a "$LOGFILE"
