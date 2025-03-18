## langchain-rag

This is a forked and updated version of [pixegami's rag tutorial v2](https://github.com/pixegami/rag-tutorial-v2). 

It features the following highlights:
- Local same machine or local network Ollama server for running model (encoding & prompt)
- Uses unsturctured to load documents which will run a model locally on the machine to conduct chunking.
- One file 'config.py' to house configuration settings (model selections, server info, etc)
- Supports langchain v0.3
- Uses chromadb for vector store
- By using unstructured more document formats than pdf are supported and chunking the documents can be done following sections vs based pages or text blocks. This is also more computationally expensive. 

## Setup
I have this running on two machines. This is not fast, but allows for experimentation as a personal project with on hand equipment that has other primary purposes. 

Machine A (software dev + host)
- Hardware: Lenovo m920q (CPU=i5-8500T, RAM=32GB)
- OS: Linux Mint virtual machine on ProxMox (CPU=4 cores & RAM=24 GB)
- Python: 3.10.12 (venv)

Machine B (ollama server)
- Hardware: CPU=Xeon W3690, GPU=GTX 1060 6GB, RAM=48GB
- OS: Win10

## Notes
For larger document sets (encoding runs thats take over 30 hrs) I have seen ollama hang / time out and python on the host ignore this and contiune waiting. To avoid this use smaller document sets or split document sets in to batches and run as an update. 
