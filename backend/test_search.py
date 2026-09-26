import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="tickets")

query = "my payment did not go through"
query_embedding = model.encode([query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=3
)

print("Query:", query)
print("\nTop 3 similar tickets:\n")
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print("Category:", meta["category"], "| Priority:", meta["priority"])
    print("Description:", doc[:150], "...")
    print("Resolution:", meta["resolution"])
    print("---")