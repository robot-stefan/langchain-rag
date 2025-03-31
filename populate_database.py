import argparse, shutil, io, os, base64

from langchain import hub
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_community.document_loaders.parsers import LLMImageBlobParser
from langchain_ollama import OllamaLLM

from config import configSetting

def main():

    # Check if the database should be reset/cleared/wipe (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", 
                        help="Reset the database.")
    parser.add_argument("--add_ollama", action="store_true", 
                        help="Build the database using ollama.")
    parser.add_argument("--add_mistral", action="store_true", 
                        help="Build the database using mistral cloud.")
    parser.add_argument("--docs_folder", action="store", type=str, default=configSetting.documentPath, 
                        help="Folder where documents are located.")
    parser.add_argument("--chroma_folder", action="store", type=str, default=configSetting.chromaPath, 
                        help="Folder where chromadb is located.")

    args = parser.parse_args()

    if args.reset:
        print("--> Wipeing Database")
        wipeDatabase(args.chroma_folder)
        print("--> Wipe Complete !!!")

    elif args.add_ollama:
        print("--> Adding Documents to Database")
        buildChromadb(args.docs_folder, args.chroma_folder, configSetting.embeddings)
        print("--> Adding Documents Complete !!!")
    
    # Comment out below elif to disable cloud option
    elif args.add_mistral:
        from configCloud import configCloudSetting # Comment out to disable clould option
        print("--> Adding Documents to Database")
        buildChromadb(args.docs_folder, args.chroma_folder, configCloudSetting.embeddingsCloudMistral)
        print("--> Adding Documents Complete !!!")


def filesList(documentPath):
    # Create list of files in directory
    filesList = os.listdir(documentPath) 
    return [documentPath + "/" + x  for x in filesList]

def fileLoad(file):
    loader = UnstructuredLoader(
        file_path=file,
        strategy="hi_res",
        mode="elements",
        add_start_index=True,
        chunking_strategy="by_title",
        max_characters=1500,
        multipage_sections=True,
        # show_progress_bar=True,
        # infer_table_structure=True,
        hi_res_model_name="yolox"
    )

    return loader.load()

def calculate_chunk_ids(chunks):

    # This will create IDs like "data/monopoly.pdf:6:2"
    # Page Source : Page Number : Chunk Index

    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page_number")
        # section = chunk.metadata.get("parent_id")
        current_page_id = f"{source}:pg.{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks

def wipeDatabase(chromaPath):
    chromaFolder = f"{configSetting.topPath}/{chromaPath}"
    if os.path.exists(chromaFolder):
        shutil.rmtree(chromaFolder)

def buildChromadb(documentPath, chromaPath, embeddings):
    ## Add each file one by one to allow for partial success of large file batches in the event of an error. 
    docsFolder = f"{configSetting.topPath}/{documentPath}"
    chromaFolder = f"{configSetting.topPath}/{chromaPath}"

    # Set database info
    db = Chroma(
        persist_directory=chromaFolder,
        embedding_function=embeddings,
    )

    # Get list of items from database
    currentItems = db.get(include=[])  # IDs are always included by default
    currentItemIds = set(currentItems["ids"])
    print(f"--> Number of existing items in DB: {len(currentItemIds)}")
    
    # Get list of files in the directory & iterate through each file in the list
    files = filesList(docsFolder)
    currentFileCounter = 1
    totalFileCount = len(files)
    for file in files:
        print(f"--> Currently loading file: [{currentFileCounter} / {totalFileCount}] - {file}")
        chunks = fileLoad(file)
        chunksWithId = calculate_chunk_ids(chunks)
        
        # Build list of new chunks not in database 
        new_chunks = []
        for chunk in chunksWithId:
            if chunk.metadata["id"] not in currentItemIds:
                new_chunks.append(chunk)
                
        if len(new_chunks):
            print(f"--> Encoding {len(new_chunks)} new chunks from: [{currentFileCounter} / {totalFileCount}] - {file}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            db.add_documents(filter_complex_metadata(new_chunks), ids=new_chunk_ids)
            print(f"--> Done adding chunks from: [{currentFileCounter} / {totalFileCount}] - {file}")
        else:
            print(f"--> No new chunks to add from: [{currentFileCounter} / {totalFileCount}] - {file}")

        currentFileCounter+= 1
    
    print(f"--> Done adding documents from {docsFolder}")


if __name__ == "__main__":
    main()