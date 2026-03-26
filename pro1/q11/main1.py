"""
The Signal — Automated Solver (Fixed)
=======================================
- NO progress file (session won't expire, we want min actions)
- Learns directions dynamically from /look responses
- Fetches map from /signal/map (no hardcoded rooms)
- Collects all items, crafts, solves all 4 puzzles
- Gets JWT token

Usage:
  1. Go to game site, enter email, click Start
  2. Get session token from browser console:
       Object.entries(sessionStorage).map(([k,v]) => k+': '+v).join('\n')
  3. Paste token into SESSION_TOKEN below
  4. Run: python3 signal.py

To clear/reset session (browser console):
  fetch('https://tds-network-games.sanand.workers.dev/signal/clear', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({email: '23f3003994@ds.study.iitm.ac.in', week: '2026-W13'})
  }).then(r => r.json()).then(console.log)
"""

import requests
import re
from collections import deque

# ── CONFIG ────────────────────────────────────────────────
SESSION_TOKEN = "0b10a81a-43fb-4477-bc87-c2f54de738a0"  # <-- paste current token
EMAIL         = "23f3003994@ds.study.iitm.ac.in"
BASE          = "https://tds-network-games.sanand.workers.dev/signal"

HEADERS = {
    "Content-Type": "application/json",
    "X-Session-Token": SESSION_TOKEN
}

# ── Known crafting recipes ─────────────────────────────────
RECIPES = [
    ("FREQUENCY_TUNER", "POWER_CELL"),      # -> POWERED_TUNER
    ("CLEANING_CLOTH",  "SOLVENT_BOTTLE"),  # -> DEMAGNETISER
    ("DEMAGNETISER",    "ACCESS_CARD"),     # -> REPAIRED_ACCESS_CARD
]

# ── State (in-memory only, no file) ───────────────────────
current_room    = "ENTRANCE_HALL"
inventory       = {}   # item_name -> description
fragments       = {}   # "PUZZLE_1_PIN" -> "A3XX" etc
puzzles         = {}   # "PUZZLE_1_PIN" -> True/False
actions_used    = 0

# Directions learned from /look responses
# room_id -> { neighbor_room -> direction }
room_directions = {}

# Lock info from /signal/map
# (from_room, to_room) -> required item or None
lock_info       = {}

# ── API calls ─────────────────────────────────────────────
def api_start():
    r = requests.post(f"{BASE}/start", headers=HEADERS, json={"email": EMAIL})
    return r.json()

def api_map():
    r = requests.get(f"{BASE}/map", headers=HEADERS)
    return r.json()

def api_look():
    r = requests.get(f"{BASE}/look", headers=HEADERS)
    return r.json()

def api_move(direction):
    r = requests.post(f"{BASE}/move", headers=HEADERS, json={"direction": direction})
    return r.json()

def api_take(item):
    r = requests.post(f"{BASE}/take", headers=HEADERS, json={"item": item})
    return r.json()

def api_examine(target):
    r = requests.get(f"{BASE}/examine", headers=HEADERS, params={"target": target})
    return r.json()

def api_combine(item_a, item_b):
    r = requests.post(f"{BASE}/combine", headers=HEADERS,
                      json={"item_a": item_a, "item_b": item_b})
    return r.json()

def api_use(target, value=None, inputs=None):
    payload = {"target": target}
    if value  is not None: payload["value"]  = value
    if inputs is not None: payload["inputs"] = inputs
    r = requests.post(f"{BASE}/use", headers=HEADERS, json=payload)
    return r.json()

# ── Map building ──────────────────────────────────────────
def load_lock_info():
    """Load locked doors and requirements from /signal/map."""
    global lock_info
    map_data = api_map()
    lock_info = {}
    for conn in map_data.get("connections", []):
        if conn.get("locked"):
            key = (conn["from"], conn["to"])
            lock_info[key] = conn.get("requires")
    print(f"  Locked doors: {lock_info}")

def update_directions(room_id, look_data):
    """
    Store directions learned from a /look response.
    exits = {"north": {"to": "SERVER_ROOM_A"}, "east": {"to": "STORAGE_ROOM"}}
    -> room_directions["ENTRANCE_HALL"]["SERVER_ROOM_A"] = "north"
    -> room_directions["ENTRANCE_HALL"]["STORAGE_ROOM"]  = "east"
    """
    if room_id not in room_directions:
        room_directions[room_id] = {}
    for direction, exit_info in look_data.get("exits", {}).items():
        neighbor = exit_info["to"]
        room_directions[room_id][neighbor] = direction

# ── Navigation ────────────────────────────────────────────
def can_pass(from_room, to_room):
    """True if we can move from from_room to to_room with current inventory."""
    requires = lock_info.get((from_room, to_room))
    if not requires:
        return True
    return requires in inventory

def find_path(start, goal):
    """BFS using room_directions. Returns [(direction, room), ...] or None."""
    if start == goal:
        return []
    queue = deque([(start, [])])
    seen  = {start}
    while queue:
        room, path = queue.popleft()
        for neighbor, direction in room_directions.get(room, {}).items():
            if neighbor in seen:
                continue
            if not can_pass(room, neighbor):
                continue
            new_path = path + [(direction, neighbor)]
            if neighbor == goal:
                return new_path
            seen.add(neighbor)
            queue.append((neighbor, new_path))
    return None

def navigate_to(target):
    """Move to target room step by step, learning directions along the way."""
    global current_room, actions_used

    if current_room == target:
        return True

    path = find_path(current_room, target)
    if path is None:
        print(f"  [nav] No known path to {target} from {current_room}")
        return False

    print(f"  {current_room} → {target}: {[d for d,_ in path]}")
    for direction, next_room in path:
        r = api_move(direction)
        actions_used = r.get("actions_used", actions_used)
        current_room = r.get("current_room", next_room)

        # Learn directions from look after each move
        look_r = api_look()
        actions_used = look_r.get("actions_used", actions_used)
        update_directions(current_room, look_r)

        print(f"    {direction} → {current_room}")

    return current_room == target

# ── Item collection ───────────────────────────────────────
def collect_here():
    """Take all items in current room and examine each for clues."""
    look_r = api_look()
    update_directions(current_room, look_r)
    items_here = look_r.get("items_here", [])

    for item in items_here:
        if item in inventory:
            continue
        api_take(item)
        exam_r = api_examine(item)
        desc   = exam_r.get("description", "")
        inventory[item] = desc
        print(f"    + {item}")

# ── Crafting ──────────────────────────────────────────────
def craft_all():
    """Try all recipes until nothing new can be crafted."""
    changed = True
    while changed:
        changed = False
        for item_a, item_b in RECIPES:
            if item_a in inventory and item_b in inventory:
                r = api_combine(item_a, item_b)
                if r.get("success"):
                    output = r["output"]
                    inventory.pop(item_a)
                    inventory.pop(item_b)
                    inventory[output] = r.get("message", "")
                    print(f"    ✓ Crafted {output}")
                    changed = True

# ── Puzzle solvers ────────────────────────────────────────
def solve_puzzle1():
    """PIN = inspection year + circled floor number."""
    if puzzles.get("PUZZLE_1_PIN"):
        return True

    cert = inventory.get("INSPECTION_CERTIFICATE", "")
    note = inventory.get("NOTEBOOK", "")
    if not cert or not note:
        return False

    # Year from certificate
    m = re.search(r"[Ii]nspection date[:\s]+(\d{4})", cert)
    if not m:
        m = re.search(r"\b(20\d{2}|19\d{2})\b", cert)
    if not m:
        print("  [P1] Cannot parse year")
        return False
    year = int(m.group(1))

    # Sublevel/floor from notebook
    m2 = re.search(r"floor number\s+(\d+)\s+is circled", note, re.IGNORECASE)
    if not m2:
        m2 = re.search(r"(\d+)\s+is circled", note, re.IGNORECASE)
    if not m2:
        m2 = re.search(r"[Ll]evel\s+(\d+)\s+sublevel", note)
    if not m2:
        m2 = re.search(r"sublevel[^\d]+(\d+)", note, re.IGNORECASE)
    if not m2:
        print(f"  [P1] Cannot parse sublevel from notebook")
        return False

    sublevel = int(m2.group(1))
    pin = year + sublevel
    print(f"  Puzzle 1: {year} + {sublevel} = PIN {pin}")

    navigate_to("SERVER_ROOM_A")
    r = api_use("PIN_TERMINAL", value=pin)
    if r.get("success"):
        frag = r["fragment_revealed"]
        fragments["PUZZLE_1_PIN"] = frag
        puzzles["PUZZLE_1_PIN"]   = True
        print(f"  ✓ Fragment 1 = {frag}")
        return True
    print(f"  ✗ Puzzle 1 failed: {r}")
    return False


def solve_puzzle2():
    """FREQUENCY = only frequency common to both SIGNAL_LOG and BACKUP_LOG."""
    if puzzles.get("PUZZLE_2_FREQUENCY"):
        return True

    if "POWERED_TUNER" not in inventory:
        print("  [P2] Need POWERED_TUNER")
        return False

    sig = inventory.get("SIGNAL_LOG", "")
    bak = inventory.get("BACKUP_LOG", "")
    if not sig or not bak:
        print("  [P2] Missing SIGNAL_LOG or BACKUP_LOG")
        return False

    sig_freqs = set(re.findall(r"(\d+\.\d+)\s*MHz", sig))
    bak_freqs = set(re.findall(r"(\d+\.\d+)\s*MHz", bak))
    common    = sig_freqs & bak_freqs

    if not common:
        print(f"  [P2] No common frequency! sig={sig_freqs} bak={bak_freqs}")
        return False

    freq = float(sorted(common)[0])
    print(f"  Puzzle 2: common frequency = {freq} MHz")

    navigate_to("MAINTENANCE_BAY")
    r = api_use("RADIO_TRANSMITTER", value=freq)
    if r.get("success"):
        frag = r["fragment_revealed"]
        fragments["PUZZLE_2_FREQUENCY"] = frag
        puzzles["PUZZLE_2_FREQUENCY"]   = True
        print(f"  ✓ Fragment 2 = {frag}")
        return True
    print(f"  ✗ Puzzle 2 failed: {r}")
    return False


def solve_puzzle3():
    """VERIFY = submit Fragment1 + Fragment2 to TERMINAL_3."""
    if puzzles.get("PUZZLE_3_VERIFY"):
        return True

    f1 = fragments.get("PUZZLE_1_PIN")
    f2 = fragments.get("PUZZLE_2_FREQUENCY")
    if not f1 or not f2:
        print(f"  [P3] Need fragments 1+2. Have: {fragments}")
        return False

    print(f"  Puzzle 3: [{f1}, {f2}] → TERMINAL_3")
    navigate_to("CONTROL_ROOM")
    r = api_use("TERMINAL_3", inputs=[f1, f2])
    if r.get("success"):
        frag = r["fragment_revealed"]
        fragments["PUZZLE_3_VERIFY"] = frag
        puzzles["PUZZLE_3_VERIFY"]   = True
        print(f"  ✓ Fragment 3 = {frag}")
        if r.get("door_unlocked"):
            print(f"  ✓ Door unlocked: {r['door_unlocked']}")
        return True
    print(f"  ✗ Puzzle 3 failed: {r}")
    return False


def solve_puzzle4():
    """PASSCODE = Fragment1 + Fragment2 + Fragment3 → EXIT_KEYPAD."""
    f1 = fragments.get("PUZZLE_1_PIN")
    f2 = fragments.get("PUZZLE_2_FREQUENCY")
    f3 = fragments.get("PUZZLE_3_VERIFY")
    if not all([f1, f2, f3]):
        print(f"  [P4] Missing fragments: {fragments}")
        return None

    passcode = f1 + f2 + f3
    print(f"  Puzzle 4: passcode = {passcode}")

    navigate_to("CORE_CHAMBER")
    r = api_use("EXIT_KEYPAD", value=passcode)
    if r.get("success"):
        puzzles["PUZZLE_4_PASSCODE"] = True
        print(r)
        
        return (r.get("completion_token") or r.get("jwt") or r.get("token"))
    print(f"  ✗ Puzzle 4 failed: {r}")
    return None


# ── Main ──────────────────────────────────────────────────
def solve():
    global current_room, actions_used

    print("=== The Signal — Automated Solver ===")
    print(f"Email: {EMAIL}\n")

    # 1. Start session
    print("[1] Starting session...")
    r = api_start()
    current_room = r.get("current_room", "ENTRANCE_HALL")
    actions_used = r.get("actions_used", 0)
    print(f"  Room: {current_room}")

    # 2. Load lock info from map
    print("\n[2] Loading map...")
    load_lock_info()

    # 3. Learn directions from starting room
    look_r = api_look()
    update_directions(current_room, look_r)

    # 4. Visit rooms in efficient order to collect everything
    # This order minimises backtracking while hitting all rooms
    visit_order = [
        "ENTRANCE_HALL",    # FACILITY_MAP, MAINTENANCE_KEY
        "SERVER_ROOM_A",    # INSPECTION_CERTIFICATE, NOTEBOOK → solve P1
        "SERVER_ROOM_B",    # UV_TORCH, ACCESS_CARD, SYSTEM_BADGE, TORN_MANUAL
        "MAINTENANCE_BAY",  # SPECIMEN_KEY, FREQUENCY_TUNER
        "POWER_ROOM",       # POWER_CELL, CLEANING_CLOTH, SOLVENT_BOTTLE, BROKEN_RADIO
        "STORAGE_ROOM",     # DRIED_MARKER
        "LABORATORY",       # (any items here)
        "CONTROL_ROOM",     # TERMINAL_3 for P3
        "ARCHIVE_ROOM",     # SIGNAL_LOG, BACKUP_LOG → solve P2
    ]

    print("\n[3] Exploring and collecting...")
    for room in visit_order:
        print(f"\n  [{room}]")
        if not navigate_to(room):
            print(f"  Cannot reach {room} — skipping")
            continue
        collect_here()
        craft_all()

        # Solve P1 as soon as items available
        if (not puzzles.get("PUZZLE_1_PIN") and
                "INSPECTION_CERTIFICATE" in inventory and
                "NOTEBOOK" in inventory):
            print("  → Solving Puzzle 1...")
            solve_puzzle1()

        # Solve P2 as soon as items available
        if (not puzzles.get("PUZZLE_2_FREQUENCY") and
                "POWERED_TUNER" in inventory and
                "SIGNAL_LOG" in inventory and
                "BACKUP_LOG" in inventory):
            print("  → Solving Puzzle 2...")
            solve_puzzle2()

    # 5. Solve any remaining puzzles
    print("\n[4] Finalising puzzles...")
    if not puzzles.get("PUZZLE_1_PIN"):
        solve_puzzle1()
    if not puzzles.get("PUZZLE_2_FREQUENCY"):
        solve_puzzle2()
    if not puzzles.get("PUZZLE_3_VERIFY"):
        solve_puzzle3()

    # 6. Refresh lock info (P3 may have unlocked CORE_CHAMBER door)
    print("\n[5] Refreshing map locks...")
    load_lock_info()
    navigate_to("CONTROL_ROOM")
    look_r = api_look()
    update_directions("CONTROL_ROOM", look_r)

    # 7. Final puzzle
    print("\n[6] Final puzzle...")
    token = solve_puzzle4()

    print(f"\nActions used: {actions_used}")
    print(f"Fragments: {fragments}")

    if token:
        print(f"\n{'='*60}")
        print("JWT TOKEN:")
        print(token)
        print("="*60)
    else:
        print("\nNo token — check errors above")
        print(f"Puzzles: {puzzles}")
        print(f"Inventory: {list(inventory.keys())}")


if __name__ == "__main__":
    solve()