import requests
import json

# Paste your complete signature here
# (masked signature with 7 chars filled in from script 1)
SIGNATURE = "aKKvsqLrrwj6pEjmhp9EHGkQ36Q6mhAoYgQ7SFVv1BD8JfVjSDncdWNTWtqxkQrfT7GhHiSZ7CN6do8LQy2CACx"

print(f"Looking up transaction: {SIGNATURE}")
print("Querying Solana Devnet...\n")

# Query Solana Devnet RPC
url = "https://api.devnet.solana.com"

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "getTransaction",
    "params": [
        SIGNATURE,
        {
            "encoding": "jsonParsed",
            "maxSupportedTransactionVersion": 0
        }
    ]
}

response = requests.post(url, json=payload)
data = response.json()

# Extract the transfer instruction
instructions = data['result']['transaction']['message']['instructions']

from_address = None
to_address = None
lamports = None

for instruction in instructions:
    if instruction.get('program') == 'system':
        info = instruction['parsed']['info']
        from_address = info['source']
        to_address = info['destination']
        lamports = info['lamports']
        break

# Convert lamports to SOL
sol_amount = lamports / 1_000_000_000

print(f"FROM:   {from_address}")
print(f"TO:     {to_address}")
print(f"AMOUNT: {lamports} lamports = {sol_amount} SOL")

print("\n--- SUBMIT THIS JSON ---")
print(json.dumps({
    "from": from_address,
    "to": to_address,
    "amount": str(sol_amount)
}, indent=2))