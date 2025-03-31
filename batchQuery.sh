# !/bin/bash

# Script for asking cucv questions
# Remember to chmod +x 

echo "Starting shell script!"

source .venv/bin/activate

echo "--->Query batch starting!!!"

# No flag is needed for local prompt processing
python query_data.py "QUESTION TEXT" --chroma_folder 01-data-chroma 

# Use --cloud to prompt with mistral.ai cloud provider
python query_data.py "QUESTION TEXT" --chroma_folder 02-data-chroma --cloud


echo "--->Query batch COMPLETE!!!"

