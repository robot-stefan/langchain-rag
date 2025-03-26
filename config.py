from langchain_ollama import OllamaEmbeddings

## This file contains configuration information for the files, server, and models used.

## Setup Environment
# Server address or IP where ollama is hosted. 
# This is assuming a self hosted server either on localhost or on a different machine on a local network. 
# Note: If not locally hosted you may need to change firewalls so that ollama will be reachable externally.
ollamaServer = "http://127.0.0.1:11434/"

# Folder names for the documents and chromadb store. If placed somwhere outside of the 
# folder containing these python files they will need to have a full directory "/some/folder".
chromaPath = "test-data-chroma"
documentPath = "test-data-docs""


## Setup Local Embedding
# Model used for building the embeddings
# embeddingsModel = "mxbai-embed-large:335m"
embeddingsModel = "mistral-small:24B"
# embeddingsModel = "llama3.2:3B"
# embeddingsModel = "mistrallite:7B"
# embeddingsModel = "nomic-embed-text"
# embeddingsModel = "deepseek-r1:32B"
# embeddingsModel = "mixtral:8x7B"
# embeddingsModel = "granite3.2-vision:2B"
# embeddingsModel = "minicpm-v:8B"

# Embedding Call
embeddings = OllamaEmbeddings(base_url=ollamaServer, model=embeddingsModel)

## Query Configuation
# Model used to process the prompt for the LLM and respond to the query
# queryModel = "llama3.3:70B"
queryModel = "mistral-small:24B"
# queryModel = "qwen2.5:32B"
# queryModel = "llama3.1:8B"
# queryModel = "llama3.2:3B"
# queryModel = "deepseek-r1:32B"

queryTemperature = 0.35
queryContextNumber = 1024
querySimilarityScore = 10
