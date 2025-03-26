import os, getpass
from langchain_mistralai import MistralAIEmbeddings


## Cloud Embeddings Setup
MISTRALAI_API_KEY = ""
embeddingsCloudMistral = MistralAIEmbeddings(model="mistral-embed", api_key=MISTRALAI_API_KEY)

# if not os.environ.get("MISTRALAI_API_KEY"):
#   os.environ["MISTRALAI_API_KEY"] = getpass.getpass("Enter API key for MistralAI: ")
# embeddingsCloudMistral = MistralAIEmbeddings(model="mistral-embed")