# !/bin/bash

# A simple bash script to add a few folders of documents
# Remember to chmod +x batchPopulate.sh

echo "Starting shell script!"

source .venv/bin/activate
python populate_database.py --docs_folder test-data-docs1 --chroma_folder test-data-chroma1 --add_ollama
python populate_database.py --docs_folder test-data-docs2 --chroma_folder test-data-chroma2 --add_ollama
python populate_database.py --docs_folder test-data-docs3 --chroma_folder test-data-chroma3 --add_ollama

echo "Shell script END!"
