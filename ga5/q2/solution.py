# /// script
# requires-python = ">=3.11"
# dependencies = ["sentence-transformers", "Pillow", "numpy"]
# ///
#uv run solution.py
import numpy as np
from PIL import Image
from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim
import os


TEXT_QUERY = "tall coastal lighthouse beacon on a rocky ocean cliff"


# ----------------------------
# Load CLIP model
# ----------------------------

model = SentenceTransformer("clip-ViT-B-32")


# ----------------------------
# Load images
# ----------------------------
#02d means 2-digit zero-padded numbers, so it generates img_01.jpg, img_02.jpg, ..., img_10.jpg
image_files = [f"img_{i:02d}.jpg" for i in range(1, 11)]

images = []
for file in image_files:
    # this assumes the images are in a folder named "q-multimodal-image-search" in the current directory
    img = Image.open(f"q-multimodal-image-search/{file}")
    images.append(img)


# ----------------------------
# Encode images
# ----------------------------
#convert_to_tensor=True means the output will be a PyTorch tensor, which is needed for cosine similarity calculation later. 
# If False, it would return a NumPy array instead.
image_embeddings = model.encode(images, convert_to_tensor=True)
#this will give us a tensor of shape (10, 512) if the model produces 512-dimensional embeddings, where each row corresponds to an image embedding.

# ----------------------------
# Encode text query
# ----------------------------

text_embedding = model.encode(TEXT_QUERY, convert_to_tensor=True)
#this will be a tensor of shape (512,) representing the embedding of the text query.

# ----------------------------
# Compute cosine similarity
# ----------------------------

similarities = cos_sim(text_embedding, image_embeddings)[0]
# cos_sim returns a 2D similarity matrix ((1,10) coz 1 text query vs 10 images )comparing the text embedding with all image embeddings.
#[[0.21, 0.45, 0.78, 0.33, ...]]
# [0] selects the first (and only) row to get a 1D list of similarity scores for the 10 images.

# ----------------------------
# Find best match
# ----------------------------

best_idx = int(np.argmax(similarities))
best_image = image_files[best_idx]


# ----------------------------
# Print result
# ----------------------------

print(best_image)