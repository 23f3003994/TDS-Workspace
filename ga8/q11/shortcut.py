import hashlib

EMAIL = "23f3003994@ds.study.iitm.ac.in"

sentences = [
    "The worst flight experience ever, delayed for hours with no communication.",
    "She did an excellent job organizing the event, everything was perfect.",
    "The hotel room was dirty, smelled bad, and had cockroaches in the bathroom."
]

# obvious labels
all_labels = ["NEGATIVE", "POSITIVE", "NEGATIVE"]

total_words = sum(len(s.split()) for s in sentences)
total_chars = sum(len(s) for s in sentences)

labels_csv = ",".join(all_labels)
verify_input = f"{EMAIL}:{labels_csv}:{total_words}:{total_chars}"
verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]

print(f"Labels: {labels_csv}")
print(f"Total words: {total_words}")
print(f"Total chars: {total_chars}")
print(f"Verify hash: {verify_hash}")
print(f"\nSubmit: {labels_csv},{total_words},{verify_hash}")