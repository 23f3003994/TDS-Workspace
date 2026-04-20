import subprocess
import time

def check_pin_time(pin, runs=10):
    """Run pin_checker multiple times and return average time"""
    pin = str(pin).zfill(8)
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        result = subprocess.run(
            ["./pin_checker"],
            input=pin,
            capture_output=True,
            text=True
        )
        end = time.perf_counter()
        times.append(end - start)
    avg = sum(times) / len(times)
    return avg, result.stdout

# Find PIN one digit at a time
found_pin = ""

for position in range(8):
    print(f"\n--- Finding digit {position+1} ---", flush=True)
    best_digit = 0
    best_time = 0

    for digit in range(10):
        # Build test PIN: correct digits so far + current guess + zeros
        test_pin = found_pin + str(digit) + "0" * (7 - position)
        avg_time, output = check_pin_time(test_pin)
        print(f"  {test_pin} → {avg_time:.4f}s", flush=True)

        if avg_time > best_time:
            best_time = avg_time
            best_digit = digit

    found_pin += str(best_digit)
    print(f"  ✓ Digit {position+1} = {best_digit} | PIN so far: {found_pin}", flush=True)

print(f"\n🎉 Found PIN: {found_pin}")

# Verify the PIN
print("\nVerifying...")
result = subprocess.run(
    ["./pin_checker"],
    input=found_pin,
    capture_output=True,
    text=True
)
print(result.stdout)