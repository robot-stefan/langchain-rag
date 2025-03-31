from populate_database import buildChromadb
from config import configSetting
# from configCloud import configCloudSetting # Comment out to disable clould option

# For constructing a batch with a handful of folders. A sufficent number of folders would be better to loop through.

documentFolderName1 = "01-data-docs"
chromaFolerName1 = "01-data-chroma"

documentFolderName2 = "02-data-docs"
chromaFolerName2 = "02-data-chroma"

documentFolderName3 = "03-data-docs"
chromaFolerName3 = "03-data-chroma"

print("--> Adding Documents to Database")
buildChromadb(documentFolderName1, chromaFolerName1, configSetting.embeddings)
print("--> Adding Folder 1 Complete !!!")
buildChromadb(documentFolderName2, chromaFolerName2, configSetting.embeddings)
print("--> Adding Folder 2 Complete !!!")
buildChromadb(documentFolderName3, chromaFolerName3, configSetting.embeddings)
print("--> Adding Folder 3 Complete !!!")
print("--> Adding All Documents Complete !!!")