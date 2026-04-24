import hashlib

EMAIL = "23f3003994@ds.study.iitm.ac.in"

name = "Frank Johansson"
age = 37
city = "Mumbai"
role = "ML engineer"
company = "Spotify"

verify_input = f"{EMAIL}:{name}:{age}:{city}:{role}:{company}"
verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]

print(f"Submit: {name},{age},{city},{role},{company},{verify_hash}")