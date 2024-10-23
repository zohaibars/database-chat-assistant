import chromadb
from pprint import pprint
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.core.extractors import TitleExtractor
from llama_index.core import SummaryIndex, VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from app.utils.connections import chromadb_connection
from llama_index.core import Settings
from llama_index.llms.groq import Groq

api_key="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"
llm = Groq(model="llama3-8b-8192",
    api_key=api_key,
    temperature=0.5
)
embediing_model = HuggingFaceEmbedding(model_name='thenlper/gte-base')
Settings.llm = llm
Settings.embed_model=embediing_model


def data_ingestion():
    """
        Ingests the documents into a vectorDB.In this case chromaDb.
    """
    splitter = SemanticSplitterNodeParser(
    buffer_size=1, breakpoint_percentile_threshold=95, 
    embed_model=embediing_model
    )
    nodes = splitter.get_nodes_from_documents(documents)
    pprint(nodes[12].metadata, indent=4)
    
    return 0

def store_documents(nodes, summary_collection, vector_collection):
    """
    Store documents in summary and vector collections.
    """
    for node in nodes:
        # Store in summary collection
        document_id = node["id"]
        if not summary_collection.get(document_id):
            summary_collection.add(id=document_id, data=node)
            print(f"Document '{document_id}' stored in summary collection.")
        else:
            print(f"Document '{document_id}' already exists in summary collection.")

        # Store in vector collection
        vector_index = VectorStoreIndex([node], show_progress=False)
        vector_index_data = vector_index.serialize()
        vector_collection.add(id=document_id, data=vector_index_data)
        print(f"Document '{document_id}' stored in vector collection.")

def query_documents(query, summary_collection, vector_collection):
    """
    Query documents based on user's question using the index stored in vector collection.
    """
    results = []
    # Use the vector index to find similar documents
    vector_index = VectorStoreIndex([])
    for document_id, data in vector_collection.iter_all():
        vector_index.deserialize(data)
        # Get similar documents based on the query
        similar_documents = vector_index.query(query, top_k=5)
        results.extend(similar_documents)
    return results

# Example usage
def main():
    nodes = [
        {"id": "node1", "text": "This is the first document."},
        {"id": "node2", "text": "This is the second document."},
    ]

    summary_collection = chromadb_connection("summary_collection")
    vector_collection = chromadb_connection("vector_collection")

    # Store documents
    store_documents(nodes, summary_collection, vector_collection)

    # Query documents based on user's question
    user_query = input("Enter your question: ")
    results = query_documents(user_query, summary_collection, vector_collection)
    if results:
        print("Matching documents found:")
        for result in results:
            print(result)
    else:
        print("No matching documents found.")

if __name__ == "__main__":
    main()
