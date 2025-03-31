# !/bin/bash

# A simple bash script to add a few folders of documents
# Remember to chmod +x batchPopulate.sh

echo "Starting shell script!"

source .venv/bin/activate

# Add with local ollama by using --add_ollama
python populate_database.py --docs_folder 01-data-docs --chroma_folder 01-data-chroma --add_ollama

# Add with cloud provider mistral.al by using --add_mistral
python populate_database.py --docs_folder 02-data-docs --chroma_folder 02-data-chroma --add_mistral

echo "Shell script END!"
