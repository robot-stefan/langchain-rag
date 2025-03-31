import numpy as np
from config import configSetting
from configCloud import configCloudSetting, MISTRALAI_API_KEY
from query_data import query_rag_local, query_rag_cloud


# A file showing batch processing and sweeping of values through a query. 

QUESTION_TEXT1 = "QUESTION TEXT 1"
QUESTION_TEXT2 = "QUESTION TEXT 2"

query_rag_local(QUESTION_TEXT1, 
          configSetting.chromaPath, 
          configSetting.embeddings, 
          configSetting.querySimilarityScore, 
          configSetting.queryTemperature, 
          configSetting.embeddingsModel, 
          configSetting.queryModel)

temperatures = np.linspace(0.10, .30, num=15)
for temperature in temperatures:
    query_rag_cloud(QUESTION_TEXT2, 
              configSetting.chromaPath, 
              configCloudSetting.embeddingsCloudMistral,  
              configCloudSetting.querySimilarityScore, 
              temperature, 
              configCloudSetting.mistralEmbeddingsModel, 
              configCloudSetting.mistralQueryModel,
              configCloudSetting.queryContextNumber, 
              MISTRALAI_API_KEY)
