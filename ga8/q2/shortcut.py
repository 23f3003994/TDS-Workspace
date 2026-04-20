import hashlib

email = "23f3003994@ds.study.iitm.ac.in"
answer = 10

print("Try submitting these in order:\n")
for steps_count in range(2, 8):
    verify_input = email + ":" + str(answer) + ":" + str(steps_count)
    verify_hash = hashlib.sha256(verify_input.encode()).hexdigest()[:14]
    print(f"{answer},{steps_count},{verify_hash}")