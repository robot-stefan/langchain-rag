import os, getpass
from langchain_mistralai import MistralAIEmbeddings
from langchain.chat_models import init_chat_model

## Set mistral API KEY or set it as OS environment flag.
MISTRALAI_API_KEY = "API_KEY_HERE"
UNSTRUCTURED_API_KEY = "API_KEY_HERE"

# if not os.environ.get("MISTRALAI_API_KEY"):
#   os.environ["MISTRALAI_API_KEY"] = getpass.getpass("Enter API key for MistralAI: ")

# if not os.environ.get("UNSTRUCTURED_API_KEY"):
#   os.environ["UNSTRUCTURED_API_KEY"] = getpass.getpass("Enter API key for Unstructured: ")

class configCloudSetting:
    pass

## Mistral (mistral.ai) model 
configCloudSetting.mistralEmbeddingsModel = "mistral-embed"
configCloudSetting.embeddingsCloudMistral = MistralAIEmbeddings(model=configCloudSetting.mistralEmbeddingsModel, 
                                                                api_key=MISTRALAI_API_KEY)

# Query Settings
configCloudSetting.mistralQueryModel = "mistral-large-latest"
configCloudSetting.queryTemperature = 0.1
configCloudSetting.queryContextNumber = 130000
configCloudSetting.querySimilarityScore = 100
configCloudSetting.queryKeywordDict = None
configCloudSetting.modelCloudMistral = init_chat_model(model=configCloudSetting.mistralQueryModel, 
                                                       model_provider="mistralai", 
                                                       temperature=configCloudSetting.queryTemperature, 
                                                       max_tokens=configCloudSetting.queryContextNumber, 
                                                       api_key=MISTRALAI_API_KEY)
