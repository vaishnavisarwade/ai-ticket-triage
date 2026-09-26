import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Step 1: Load the data (same as Day 1)
df = pd.read_csv("../data/tickets.csv")

# Step 2: Only keep tickets that have a Resolution filled in
# (we only want to search tickets that were actually solved)
df = df.dropna(subset=["Resolution"])
print("Tickets with a resolution:", len(df))

# Step 3: Load the embedding model
# This downloads a small model the first time you run it (one-time, ~80MB)
model = SentenceTransformer("all-MiniLM-L6-v2")

# Step 4: Set up ChromaDB (it will save data to a local folder)
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection(name="tickets")

# Step 5: Prepare the data for embedding
descriptions = df["Ticket Description"].tolist()
ids = [str(ticket_id) for ticket_id in df["Ticket ID"].tolist()]

# Step 6: Generate embeddings for all descriptions
print("Generating embeddings... this may take a minute")
embeddings = model.encode(descriptions).tolist()

# Step 7: Store everything in ChromaDB
collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=descriptions,
    metadatas=[
        {"category": row["Ticket Type"], "priority": row["Ticket Priority"], "resolution": row["Resolution"]}
        for _, row in df.iterrows()
    ]
)

print("Done! Stored", collection.count(), "tickets in the vector database.")