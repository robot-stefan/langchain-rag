from langchain_ollama import OllamaEmbeddings, OllamaLLM

class configSetting:
    pass

## This file contains configuration information for the files, server, and models used.

## Setup Environment
# Server address or IP where ollama is hosted. 
# This is assuming a self hosted server either on localhost or on a different machine on a local network. 
# Note: If not locally hosted you may need to change firewalls so that ollama will be reachable externally.
configSetting.ollamaServer = "http://127.0.0.1:11434/"

# Folder names for the documents and chromadb store held in the "data" folder. If placed somwhere outside of the 
# folder containing these python files topPath will need to become "/some/folder". Then the location of the files
# will become /some/folder/test-data-chroma for example. 
configSetting.topPath = "data"
configSetting.chromaPath = "test-data-chroma"
configSetting.documentPath = "test-data-docs"


## Setup Local Embedding
# Model used for building the embeddings
# configSetting.embeddingsModel = "mxbai-embed-large:335m"
# configSetting.embeddingsModel = "mistral-small:24B"
configSetting.embeddingsModel = "llama3.2:3B"
# configSetting.embeddingsModel = "mistrallite:7B"
# configSetting.embeddingsModel = "nomic-embed-text"
# configSetting.embeddingsModel = "deepseek-r1:32B"
# configSetting.embeddingsModel = "mixtral:8x7B"
# configSetting.embeddingsModel = "granite3.2-vision:2B"
# configSetting.embeddingsModel = "minicpm-v:8B"

# Embedding Call
configSetting.embeddings = OllamaEmbeddings(base_url=configSetting.ollamaServer, model=configSetting.embeddingsModel)


## Query Configuation
# Model used to process the prompt for the LLM and respond to the query
# configSetting.queryModel = "llama3.3:70B"
configSetting.queryModel = "mistral-small:24B"
# configSetting.queryModel = "qwen2.5:32B"
# configSetting.queryModel = "llama3.1:8B"
# configSetting.queryModel = "llama3.2:3B"
# configSetting.queryModel = "deepseek-r1:32B"

configSetting.queryTemperature = 0.01
configSetting.queryContextNumber = 120000
configSetting.querySimilarityScore = 100
configSetting.queryKeywordDict = None

configSetting.model = OllamaLLM(base_url=configSetting.ollamaServer, 
                  model=configSetting.queryModel, 
                  num_ctx=configSetting.queryContextNumber, 
                  temperature=configSetting.queryTemperature)
