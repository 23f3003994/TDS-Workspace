# /// script
# dependencies = [
#   "openai",
#   "scikit-learn"
# ]
# ///




# uv run solution.py

import os
from openai import OpenAI
from sklearn.cluster import KMeans


# -------------------------
# OpenAI client
# -------------------------

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://aipipe.org/openai/v1")
)


# -------------------------
# Step 1: Read product descriptions
# -------------------------

file_path = "q-embeddings-clustering.txt"

with open(file_path, "r") as f:
    descriptions = [line.strip() for line in f if line.strip()]

# now descriptions = list of 50 strings


# -------------------------
# Step 2: Generate embeddings
# -------------------------

response = client.embeddings.create(
    model="text-embedding-3-small",
    input=descriptions
)
    ## response format
        # CreateEmbeddingResponse(
        # data=[
        #     Embedding(
        #         embedding=[...],  # vector for text 1
        #         index=0,
        #         object='embedding'
        #     ),
        #     Embedding(
        #         embedding=[...],  # vector for text 2
        #         index=1,
        #         object='embedding'
        #     )
        # ],
        # model='text-embedding-ada-002',
        # object='list',
        # usage=Usage(prompt_tokens=X, total_tokens=X)
        #embedding_1 = response.data[0].embedding

        # Extract the embeddings from the response

embeddings = [item.embedding for item in response.data]


# -------------------------
# Step 3: Run KMeans
# -------------------------

kmeans = KMeans(
    n_clusters=5,
    random_state=42,
    n_init=10
)
# n_init=10 means it will run KMeans 10 times with different initial centroids 
# and choose the best one (lowest inertia)

#random_state=42 ensures reproducibility of results,
# ie the same initial centroids will be chosen each time the code is "RUN",
#  leading to the same clustering results.


labels = kmeans.fit_predict(embeddings)


# -------------------------
# Step 4: Count cluster sizes
# -------------------------

cluster_counts = {}

for label in labels:
    cluster_counts[label] = cluster_counts.get(label, 0) + 1


# -------------------------
# Step 5: Find largest cluster
# -------------------------

largest_cluster = max(cluster_counts, key=cluster_counts.get)
count = cluster_counts[largest_cluster]


# -------------------------
# Step 6: Print answer
# -------------------------

print(f"{largest_cluster}, {count}")



