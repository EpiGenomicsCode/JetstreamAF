# AlphaFold on Jetstream2 (Indiana University)

This repository contains scripts and instructions for running AlphaFold on Jetstream2 at Indiana University.

### Directory Structure

- `FASTA_Temp/`: Place your input FASTA files in this directory. The script will process all `.fa` files in this directory.
- `OUTPUT/`: The results of AlphaFold runs will be stored here.
- `run_alphafold.sh`: The automation script that runs the MSA and strcuture prediction.
- `design_tools/`: Contains the GPU and MSA scripts that are used by the run_alphafold.sh script.

### Main Script: run_alphafold.sh

This script automates the process of running AlphaFold for multiple input sequences. Here's what it does:

1. Sets up necessary directories and log files.
2. Iterates through all `.fa` files in the `FASTA_Temp/` directory.
3. For each file:
   - Checks if MSA has already been generated (looks for `features.pkl`).
   - If not, runs the MSA generation script (`run_alphafold-msa_2.3.1.py`).
   - Runs the GPU prediction script (`run_alphafold-gpu_2.3.2.py`).
   - Logs CPU and GPU usage during the run.
   - Records execution times for both MSA generation and GPU prediction.

## Setup Instructions

1. Download the Singularity image:
   - Option 1: Download from Sylabs
   - Option 2: Download from the AlphaFold website

2. Build the Singularity container in your repository.

3. Verify the contents of the `.singularity.d` directory, especially:
   - runscript
   - Singularity
   - startscript
   - Other relevant files

4. Check your version of hhblits:
   ```
   hhblits --version
   ```
   If you get an "illegal command" error, you need to update hhblits. You can get it from:
   https://github.com/soedinglab/hh-suite.git

5. Update hhblits paths in the following files:
   - `/home/vmathew/Desktop/gitrepo/JetstreamAF/design_tools/run_alphafold-gpu_2.3.2.py`
   - `/home/vmathew/Desktop/gitrepo/JetstreamAF/design_tools/run_alphafold-msa_2.3.1.py`

   Update the following line in both files. If you're not updating hhblits, remove the following lines from both files:
   ```python
   hhblits_binary = os.path.expanduser('~/hh-suite/bin/hhblits')
   ```
   
   ```python
   hhblits_binary = os.path.expanduser('~/hh-suite/bin/hhblits')
   f'--hhblits_binary_path={hhblits_binary}',
   ```

## Running AlphaFold

1. Ensure all databases and dependencies are correctly set up.

2. Ensure the following python scripts under design_tools:
   - For GPU version: `run_alphafold-gpu_2.3.2.py`
   - For MSA version: `run_alphafold-msa_2.3.1.py`

3. Modify the scripts as needed to match your specific Jetstream environment and paths.

## Important Notes

- Make sure you have the necessary permissions to run Singularity containers on Jetstream.
- Adjust paths in the scripts to match your Jetstream directory structure.
- Ensure you have sufficient storage and computational resources allocated for running AlphaFold.

## Troubleshooting

If you encounter any issues:
1. Check the Singularity container's log files.
2. Verify all paths and environment variables are correctly set.
3. Ensure all required databases are accessible and up-to-date.

For further assistance, please open an issue in this repository.
