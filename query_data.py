import argparse, shutil, io, os, base64, json, time

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from config import configSetting

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context and the fact that you enjoy playing board games. : {question}
"""


def main():
    # Create CLI.
    parser = argparse.ArgumentParser()
    parser.add_argument("query_text", type=str, 
                        help="The query text.")
    parser.add_argument("--chroma_folder", action="store", type=str, default=configSetting.chromaPath, 
                        help="Folder where chromadb is located.")
    parser.add_argument("--temperature", action="store", type=int, default=configSetting.queryTemperature, 
                        help="Temperature for the LLM impacts how creative text generation will be  closer to 0 is less creative.")
    parser.add_argument("--context_no", action="store", type=int, default=configSetting.queryContextNumber, 
                        help="Max context size for the prompt this needs to hold the prompt and be under the limit of the model.")
    parser.add_argument("--similarity", action="store", type=int, default=configSetting.querySimilarityScore, 
                        help="Max context size for the prompt this needs to hold the prompt and be under the limit of the model.")
    parser.add_argument("--cloud", action="store_true", 
                        help="Use cloud embedding and provider for prompt response.")

    args = parser.parse_args()
    query_text = args.query_text

    if args.cloud:
        from configCloud import configCloudSetting, MISTRALAI_API_KEY

        embeddingsName=configCloudSetting.mistralEmbeddingsModel
        modelName=configCloudSetting.mistralQueryModel
        
        query_rag_cloud(query_text, 
                        args.chroma_folder, 
                        configCloudSetting.embeddingsCloudMistral, 
                        args.similarity, 
                        args.temperature, 
                        embeddingsName, 
                        modelName, 
                        args.context_no, 
                        MISTRALAI_API_KEY)


    else:
        embeddingsName=configSetting.embeddingsModel
        modelName=configSetting.queryModel

        query_rag_local(query_text, 
                        args.chroma_folder, 
                        configSetting.embeddings, 
                        args.similarity, 
                        args.temperature, 
                        embeddingsName, 
                        modelName, 
                        args.context_no)


def query_rag(query_text: str, chromaPath, embeddings, model, similarity, temperature, embeddingsName, modelName):
    # Set full folder path
    chromaFolder = f"{configSetting.topPath}/{chromaPath}"
    
    # Prepare the DB.
    db = Chroma(persist_directory=chromaFolder, embedding_function=embeddings)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=similarity, where_document=configSetting.queryKeywordDict)

    # Add results to prompt for context
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    response_text = model.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    # response_only = f"{response_text}"
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    # print(formatted_response)

    # wirte response and info to json for logging
    timestamp = time.ctime()
    dictionary = {
        "response": f"{response_text.content}",
        "refrence": {
            "prompt": prompt,
            "context": context_text,
            "source": sources,
        },
        "settings": {
            "similarity_score": similarity,
            "temperature": temperature,
            "model": modelName,
            "embeddings": embeddingsName,
            "database": chromaFolder,
        },
        "metrics": {
            "source_count": len(sources),
            "time-utc": time.asctime(time.gmtime()),
            "time-local": timestamp,
        },


    }

    logFileName = f"logs/PromptReply_{timestamp}.json"
    logTextName = f"logs/PromptReply_{timestamp}.txt"

    # Serializing json
    json_object = json.dumps(dictionary, indent=1)

    # Writing to json
    with open(logFileName, "w") as outfile:
        outfile.write(json_object)
    
    # write to txt
    file = open(logTextName, "w")
    file.write(f"Response: {response_text.content}")
    file.write("\n") 
    file.close() 

    return response_text

def query_rag_local(query_text: str, chromaFolder, embeddings, similarity, temperature, embeddingsName, modelName, context_no):
        
        model = OllamaLLM(base_url=configSetting.ollamaServer, 
                          model=modelName, 
                          temperature=temperature, 
                          num_ctx=context_no)
        query_rag(query_text, 
                  chromaFolder, 
                  embeddings, 
                  model, 
                  similarity, 
                  temperature, 
                  embeddingsName, 
                  modelName)


def query_rag_cloud(query_text: str, chromaFolder, embeddings, similarity, temperature, embeddingsName, modelName, context_no, api_key):
     from langchain.chat_models import init_chat_model
     from configCloud import configCloudSetting
     modelCloudMistral = init_chat_model(model=configCloudSetting.mistralQueryModel, 
                                            model_provider="mistralai", 
                                            temperature=temperature, 
                                            max_tokens=context_no, 
                                            api_key=api_key)
     query_rag(query_text, 
                  chromaFolder, 
                  embeddings, 
                  modelCloudMistral, 
                  similarity, 
                  temperature, 
                  embeddingsName, 
                  modelName)


if __name__ == "__main__":
     main()
