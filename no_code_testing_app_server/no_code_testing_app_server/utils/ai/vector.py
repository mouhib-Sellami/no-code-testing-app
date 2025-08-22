from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import json

base_path = os.path.join(os.getcwd(), 'media', 'cases.json')

knowledge_base = json.load(open(base_path, 'r'))
embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chrome_langchain_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []
    i = 0
    for row in knowledge_base:
        document = Document(
            page_content=(row["prompt"]),
            metadata = {"test": json.dumps(row)},
            id = str(i)
        )
        ids.append(str(i))
        documents.append(document)
        i += 1
vector_store= Chroma(
    collection_name = "test_cases",
    persist_directory = db_location,
    embedding_function = embeddings
)

if add_documents:
    vector_store.add_documents(documents=documents, ids=ids)

retriever= vector_store.as_retriever(
    search_kwargs = {"k": 20}
)
