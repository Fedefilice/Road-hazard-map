#!/bin/sh

#SBATCH -J Qwen_analysis_%a  ## The name of the job (everything is ok)
#SBATCH -o ./Qwen_analysis_%a_%j.txt  ## The name of the log file (everything is ok)
#SBATCH --partition=gpu  ## Or cpu if no gpu needed.
#SBATCH --qos=gpu  ## Same as partition.
#SBATCH --ntasks=1  ## Always 1 in general.  ## Do not touch
#SBATCH --cpus-per-task=4  ## Number of CPU cores.
#SBATCH --gres=gpu:1  ## What GPU (e.g. a100_80g, a100_40g, p100 etc.), and how many GPUs. 
#SBATCH --time=0-23:59:59  ## Time limit (for GPU is 1 day, so no more than what is set).
#SBATCH --mem=30G  ## How much RAM is needed (in GB).
#SBATCH --array=0-7  ## Array job per eseguire 8 script in parallelo

module load miniconda3  ## Do not touch.
module load gnu7  ## Do not touch.
source "$CONDA_PREFIX/etc/profile.d/conda.sh"  ## Do not touch.
conda activate tesi  ## Load conda environment if any. Substitute "env_name" with the name of your environment, e.g., "tesi".

## Run python scripts.

# Array di script Python da eseguire
SCRIPTS=(
    "analisi_monolabel_few6.py"
    "analisi_monolabel_few7.py"
    "analisi_monolabel_few8.py"
    "analisi_monolabel_few9.py"
    "analisi_monolabel10.py"
    "analisi_multilabel_few2.py"
    "analisi_multilabel1.py"
    "analisi_multilabel11_few.py"
)

# Esegui lo script corrispondente all'indice dell'array
echo "Esecuzione di ${SCRIPTS[$SLURM_ARRAY_TASK_ID]}"
python ${SCRIPTS[$SLURM_ARRAY_TASK_ID]}

conda deactivate  ## Do not touch.

## Run this file from command line as "sbatch sbatch_template.sh".