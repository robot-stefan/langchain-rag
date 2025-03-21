import argparse, shutil, io, os, base64

from langchain import hub
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_ollama import OllamaLLM

from config import chromaPath, documentPath, embeddings, embeddingsDB 

def main():

    # Check if the database should be reset/cleared/wipes (using the --reset flag).
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset the database.")
    parser.add_argument("--add", action="store_true", help="Build the database.")
    args = parser.parse_args()
    if args.reset:
        print("--> Wipeing Database")
        wipeDatabase()
        print("--> Wipe Complete !!!")

    elif args.add:
        print("--> Adding Documents to Database")
        buildChromadb(documentPath, chromaPath, embeddings, embeddingsDB)
        print("--> Adding Documents Complete !!!")

def filesList(documentPath):
    # Create list of files in directory
    filesList = os.listdir(documentPath)
    return [documentPath + "/" + x  for x in filesList]

def fileLoad(file):
    loader = UnstructuredLoader(
        file_path=filesList(file),
        strategy="hi_res",
        mode="elements",
        add_start_index=True,
        chunking_strategy="by_title",
        max_characters=1500,
        multipage_sections=True,
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

def wipeDatabase():
    if os.path.exists(chromaPath):
        shutil.rmtree(chromaPath)

def buildChromadb(documentPath, chromaPath, embeddings):
    ## Add each file one by one to allow for partial success of large file batches in the event of an error. 

    # Set database info
    db = Chroma(
        persist_directory=chromaPath,
        embedding_function=embeddings,
    )

    # Get list of items from database
    currentItems = db.get(include=[])  # IDs are always included by default
    currentItemIds = set(currentItems["ids"])
    print(f"--> Number of existing documents in DB: {len(currentItemIds)}")
    
    # Get list of files in the directory & iterate through each file in the list
    files = filesList(documentPath)
    i = 1
    totalFileCount = len(files)
    for file in files:
        print(f"--> Currently loading file: [{i} / {totalFileCount}] - {file}")
        chunks = fileLoad(file)
        chunksWithId = calculate_chunk_ids(chunks)
        
        # Build list of new chunks not in database 
        new_chunks = []
        for chunk in chunksWithId:
            if chunk.metadata["id"] not in currentItemIds:
                new_chunks.append(chunk)
                
        if len(new_chunks):
            print(f"--> Adding {len(new_chunks)} new chunks from: [{i} / {totalFileCount}] - {file}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
            db.add_documents(filter_complex_metadata(new_chunks), ids=new_chunk_ids)
            print(f"--> Done adding chunks from: [{i} / {totalFileCount}] - {file}")
        else:
            print(f"--> No new chunks to add from: [{i} / {totalFileCount}] - {file}")

        i+= 1
    
    print(f"--> Done adding documents from {documentPath}")

if __name__ == "__main__":
    main()

