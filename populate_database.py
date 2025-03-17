import argparse, shutil, io, os, base64

from langchain import hub
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_unstructured import UnstructuredLoader
from langchain_community.vectorstores.utils import filter_complex_metadata
from langchain_ollama import OllamaLLM

from config import chromaPath, documentPath, embeddings 


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
        buildChromadb(documentPath, chromaPath, embeddings)
        print("--> Adding Documents Complete !!!")




## Load directory of documents & conduct chunking
# need to add for files list to only have new files
def filesList(documentPath):
    filesList = os.listdir(documentPath)
    # for a in filesList:
    #     if a == 
    return [documentPath + "/" + x  for x in filesList]

def filesLoad(documentPath):
    loader = UnstructuredLoader(
        file_path=filesList(documentPath),
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
    ## Function to build Chromadb. It checks for existing documents 
    # and old adds news ones.
    # Set and load db
    db = Chroma(
        persist_directory=chromaPath,
        embedding_function=embeddings,
    )

    # Get chunks & Ids 
    chunks = filesLoad(documentPath)
    chunksWithId = calculate_chunk_ids(chunks)
    
    # Get existing items db
    currentItems = db.get(include=[])  # IDs are always included by default
    currentItemIds = set(currentItems["ids"])
    print(f"--> Number of existing documents in DB: {len(currentItemIds)}")

    # Add new items 
    new_chunks = []
    for chunk in chunksWithId:
        if chunk.metadata["id"] not in currentItemIds:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"--> Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(filter_complex_metadata(new_chunks), ids=new_chunk_ids)
        print("--> Building chromadb complete!")
        # db.persist()
    else:
        print("--> No new documents to add")

if __name__ == "__main__":
    main()

