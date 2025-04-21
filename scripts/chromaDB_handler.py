import json
import os
import pandas as pd
import torch
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from typing import List, Dict, Any

# Define the custom embedding function
class CustomEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name: str, device: str = 'cpu'):
        self.model = SentenceTransformer(model_name, device=device, trust_remote_code=True)

    def __call__(self, texts: Documents) -> Embeddings:
        if not isinstance(texts, list):
            texts = [texts]
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()

# Define ChromaDataManager to abstract vector store interactions
class ChromaDataManager:
    def __init__(self, model_path: str, collection_name: str, data_path: str, device: str = 'cpu'):
        self.device = device
        self.embedding_function = CustomEmbeddingFunction(model_path, device=device)
        self.collection_name = collection_name
        self.data_path = data_path

        # Initialize ChromaDB client
        import chromadb  # Avoid global dependency
        self.client = chromadb.PersistentClient(path=os.path.join(data_path, "chromadb"))

        # Create or get the collection with embedding function
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(self, documents: List[str], metadatas: List[dict], ids: List[str]):
        """Adds documents and metadata to the collection."""
        try:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False

    def search_vector_store(self, query: str, n_results: int = 10):
        """Retrieves the top n matches based on the query description and returns as a DataFrame."""
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
            return self.format_search_results_as_df(results)
        except Exception as e:
            print(f"Error searching vector store: {e}")
            return None

    def format_search_results_as_df(self, results):
        """Converts the query results into a pandas DataFrame."""
        if not results or "ids" not in results:
            return pd.DataFrame()

        data = []
        for idx, _id in enumerate(results["ids"][0]):
            row = {
                "ID": _id,
                "Score": 1 - results["distances"][0][idx],
                "Text": results["documents"][0][idx]
            }
            row.update(results["metadatas"][0][idx])  # Add metadata fields dynamically
            data.append(row)

        return pd.DataFrame(data)
    

import uuid
import time
import pandas as pd
# Function to add data in batches
def add_to_chroma_batched(data_manager, data_df, doc_col, meta_cols, batch_size=1000, file_id=""):
    total_rows = len(data_df)
    num_batches = (total_rows + batch_size - 1) // batch_size
    start_time = time.perf_counter()

    for batch_num, i in enumerate(range(0, total_rows, batch_size)):
        print(f"Processing batch {batch_num + 1}/{num_batches}")
        batch_df = data_df.iloc[i:min(i + batch_size, total_rows)]
        batch_ids = [
                f"{file_id}_{idx}_{str(uuid.uuid4())[:8]}"
                for idx in batch_df.index
            ]
        try:
            success = data_manager.add_documents(
                documents=batch_df[doc_col].tolist(),
                metadatas=batch_df[meta_cols].to_dict(orient='records'),
                ids=batch_ids
            )
            if success:
                print(f"Batch {batch_num + 1} added successfully.")
            else:
                print(f"Batch {batch_num + 1} failed.")
            
        except Exception as e:
            print(f"Error in batch {batch_num + 1}: {e}")
            return False

    return True
