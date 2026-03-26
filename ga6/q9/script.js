const fs = require("fs");

// Load the JSON file from the same folder
const data = JSON.parse(fs.readFileSync("embeddings.json", "utf-8"));
// Dot product function
const dot = (a, b) => a.reduce((s, x, i) => s + x * b[i], 0);

// Vector cosine similarity = dot product (vectors are already normalized)
const counts = { paraphrase: 0, negation: 0, near_duplicate: 0 };

// Iterate over all pairs
for (const pair of data) {
  // Compute cosine similarity (dot product)
  const sim = dot(pair.embedding_a, pair.embedding_b);

  // Check if the pair fails based on the threshold and operation
  const fails = pair.threshold_op === ">=" 
    ? sim < pair.threshold  // If cosine is less than threshold for >= condition
    : sim > pair.threshold; // If cosine is greater than threshold for <= condition

  // Increment the count for failures based on pair type
  if (fails) counts[pair.type]++;
}

console.log(counts);