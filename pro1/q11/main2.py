"""
VERSION 2 -DIDNT RUN YET
The Signal — Automated Solver v2 (Hybrid)
==========================================
Improvements over v1:
1. Retry loop — runs up to 10 cycles until solved
2. Hybrid frequency — intersection first, fallback to most repeated frequency
3. Fragment recovery — reads already-solved fragments from /inventory
4. Pre-examine — reads clue item descriptions before/after taking them
5. Dynamic BFS — directions learned from /look, no hardcoding

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
SESSION_TOKEN = "472da987-19a7-4d48-b438-914a90a12829"  # <-- paste current token
EMAIL         = "23f3003994@ds.study.iitm.ac.in"
BASE          = "https://tds-network-games.sanand.workers.dev/signal"

HEADERS = {
    "Content-Type": "application/json",
    "X-Session-Token": SESSION_TOKEN
}

# ── Crafting recipes ──────────────────────────────────────
RECIPES = [
    ("FREQUENCY_TUNER", "POWER_CELL"),      # -> POWERED_TUNER
    ("CLEANING_CLOTH",  "SOLVENT_BOTTLE"),  # -> DEMAGNETISER
    ("DEMAGNETISER",    "ACCESS_CARD"),     # -> REPAIRED_ACCESS_CARD
]

# Items whose descriptions contain puzzle clues
CLUE_ITEMS = {
    "INSPECTION_CERTIFICATE",
    "NOTEBOOK",
    "SIGNAL_LOG",
    "BACKUP_LOG",
    "RESEARCH_NOTE",
}

# ── State (in-memory) ─────────────────────────────────────
current_room    = "ENTRANCE_HALL"
inventory       = {}    # item_name -> description
memory          = {}    # item_name -> description (clue items, read even before taking)
fragments       = {}    # "PUZZLE_1_PIN" -> "A3XX" etc
puzzles_solved  = {}    # puzzle_id -> True
actions_used    = 0
room_directions = {}    # room -> {neighbor_room -> direction}
lock_info       = {}    # (from, to) -> required_item

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

def api_inventory():
    r = requests.get(f"{BASE}/inventory", headers=HEADERS)
    return r.json()

# ── Map building ──────────────────────────────────────────
def load_lock_info():
    """Load locked doors from /signal/map."""
    global lock_info
    map_data = api_map()
    lock_info = {}
    for conn in map_data.get("connections", []):
        if conn.get("locked"):
            key = (conn["from"], conn["to"])
            lock_info[key] = conn.get("requires")
    all_rooms = [r["id"] for r in map_data.get("rooms", [])]
    print(f"  Rooms: {len(all_rooms)} | Locked doors: {len(lock_info)}")
    return all_rooms

def update_directions(room_id, look_data):
    """Learn directions from a /look response."""
    if room_id not in room_directions:
        room_directions[room_id] = {}
    for direction, exit_info in look_data.get("exits", {}).items():
        neighbor = exit_info["to"]
        room_directions[room_id][neighbor] = direction

# ── Navigation (BFS) ──────────────────────────────────────
def can_pass(from_room, to_room):
    requires = lock_info.get((from_room, to_room))
    if not requires:
        return True
    return requires in inventory

def find_path(start, goal):
    """BFS — returns [(direction, room), ...] or None."""
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
    """Move to target room using BFS, learning directions along the way."""
    global current_room, actions_used

    for attempt in range(40):   # max 40 steps (like JS version)
        if current_room == target:
            return True

        # Refresh directions from current room
        look_r = api_look()
        actions_used = look_r.get("actions_used", actions_used)
        update_directions(current_room, look_r)

        path = find_path(current_room, target)
        if not path:
            print(f"  [nav] No path to {target} from {current_room}")
            return False

        # Take one step
        direction, next_room = path[0]
        move_r = api_move(direction)
        actions_used = move_r.get("actions_used", actions_used)
        current_room = move_r.get("current_room", next_room)
        print(f"    {direction} → {current_room}")

    return current_room == target

# ── Item collection ───────────────────────────────────────
def scan_and_collect(room_data):
    """
    Improvement 4: Pre-examine clue items BEFORE taking them.
    Then take everything and examine non-clue items too.
    """
    items_here = room_data.get("items_here", [])

    # Pre-examine clue items (read descriptions even if we can't take)
    for item in items_here:
        if item in CLUE_ITEMS and item not in memory:
            exam_r = api_examine(item)
            desc   = exam_r.get("description", "")
            if desc:
                memory[item] = desc
                print(f"    📖 Scanned clue: {item}")

    # Take all items
    for item in items_here:
        if item in inventory:
            continue
        take_r = api_take(item)
        if take_r.get("success", True):
            # Examine to get description
            exam_r = api_examine(item)
            desc   = exam_r.get("description", "")
            inventory[item] = desc
            # Also store in memory if it's a clue item
            if item in CLUE_ITEMS:
                memory[item] = desc
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

# ── Improvement 3: Fragment recovery from /inventory ──────
def recover_fragments():
    """Read already-solved fragments directly from /inventory API."""
    inv_r = api_inventory()
    pz    = inv_r.get("puzzles", {})

    if pz.get("PUZZLE_1_PIN", {}).get("solved"):
        frag = pz["PUZZLE_1_PIN"].get("fragment")
        if frag:
            fragments["PUZZLE_1_PIN"]    = frag
            puzzles_solved["PUZZLE_1_PIN"] = True
            print(f"  ↩ Recovered Fragment 1 = {frag}")

    if pz.get("PUZZLE_2_FREQUENCY", {}).get("solved"):
        frag = pz["PUZZLE_2_FREQUENCY"].get("fragment")
        if frag:
            fragments["PUZZLE_2_FREQUENCY"]    = frag
            puzzles_solved["PUZZLE_2_FREQUENCY"] = True
            print(f"  ↩ Recovered Fragment 2 = {frag}")

    if pz.get("PUZZLE_3_VERIFY", {}).get("solved"):
        frag = pz["PUZZLE_3_VERIFY"].get("fragment")
        if frag:
            fragments["PUZZLE_3_VERIFY"]    = frag
            puzzles_solved["PUZZLE_3_VERIFY"] = True
            print(f"  ↩ Recovered Fragment 3 = {frag}")

# ── Puzzle solvers ────────────────────────────────────────
def solve_puzzle1():
    if puzzles_solved.get("PUZZLE_1_PIN"):
        return True

    cert = memory.get("INSPECTION_CERTIFICATE", "")
    note = memory.get("NOTEBOOK", "")
    if not cert or not note:
        return False

    # Parse year
    m = re.search(r"[Ii]nspection date[:\s]+(\d{4})", cert)
    if not m:
        m = re.search(r"\b(20\d{2}|19\d{2})\b", cert)
    if not m:
        print("  [P1] Cannot parse year")
        return False
    year = int(m.group(1))

    # Parse circled floor/sublevel number
    m2 = re.search(r"floor number\s+(\d+)\s+is circled", note, re.IGNORECASE)
    if not m2:
        m2 = re.search(r"(\d+)\s+is circled", note, re.IGNORECASE)
    if not m2:
        m2 = re.search(r"[Ll]evel\s+(\d+)\s+sublevel", note)
    if not m2:
        m2 = re.search(r"sublevel[^\d]+(\d+)", note, re.IGNORECASE)
    if not m2:
        # Last resort — first number in notebook
        m2 = re.search(r"\b(\d+)\b", note)
    if not m2:
        print("  [P1] Cannot parse sublevel")
        return False

    sublevel = int(m2.group(1))
    pin      = year + sublevel
    print(f"  Puzzle 1: {year} + {sublevel} = PIN {pin}")

    navigate_to("SERVER_ROOM_A")
    r = api_use("PIN_TERMINAL", value=pin)
    if r.get("success"):
        frag = r.get("fragment_revealed") or r.get("fragment")
        fragments["PUZZLE_1_PIN"]    = frag
        puzzles_solved["PUZZLE_1_PIN"] = True
        print(f"  ✓ Fragment 1 = {frag}")
        return True
    print(f"  ✗ Puzzle 1 failed: {r}")
    return False


def solve_puzzle2():
    if puzzles_solved.get("PUZZLE_2_FREQUENCY"):
        return True

    if "POWERED_TUNER" not in inventory:
        print("  [P2] Need POWERED_TUNER")
        return False

    sig = memory.get("SIGNAL_LOG", "")
    bak = memory.get("BACKUP_LOG", "")
    if not sig and not bak:
        print("  [P2] Missing both logs")
        return False

    # Parse all FM-range frequencies from all clue items
    # FM range: 70-150 MHz
    all_datasets = {}
    for item_id, desc in memory.items():
        matches = re.findall(r"(\d{2,3}(?:\.\d+)?)\s*MHz", desc)
        valid   = [v for v in matches if 70 < float(v) < 150]
        if valid:
            all_datasets[item_id] = valid

    best_freq = None

    # Strategy A: Intersection — find frequency in both logs
    keys = list(all_datasets.keys())
    if len(keys) >= 2:
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                inter = set(all_datasets[keys[i]]) & set(all_datasets[keys[j]])
                if inter:
                    best_freq = sorted(inter)[0]
                    print(f"  Puzzle 2 (intersection): {best_freq} MHz")
                    break
            if best_freq:
                break

    # Strategy B: Fallback — most repeated frequency across all logs
    if not best_freq:
        print("  [P2] Intersection failed — trying frequency mode fallback...")
        counts = {}
        for freqs in all_datasets.values():
            for v in freqs:
                counts[v] = counts.get(v, 0) + 1
        # Find most frequent
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        if sorted_counts and sorted_counts[0][1] > 1:
            best_freq = sorted_counts[0][0]
            print(f"  Puzzle 2 (mode fallback): {best_freq} MHz "
                  f"(appears {sorted_counts[0][1]} times)")

    if not best_freq:
        print(f"  [P2] Cannot determine frequency! Datasets: {all_datasets}")
        return False

    navigate_to("MAINTENANCE_BAY")
    r = api_use("RADIO_TRANSMITTER", value=float(best_freq))
    if r.get("success"):
        frag = r.get("fragment_revealed") or r.get("fragment")
        fragments["PUZZLE_2_FREQUENCY"]    = frag
        puzzles_solved["PUZZLE_2_FREQUENCY"] = True
        print(f"  ✓ Fragment 2 = {frag}")
        return True
    print(f"  ✗ Puzzle 2 failed: {r}")
    return False


def solve_puzzle3():
    if puzzles_solved.get("PUZZLE_3_VERIFY"):
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
        frag = (r.get("fragment_revealed") or r.get("fragment") or
                r.get("puzzles", {}).get("PUZZLE_3_VERIFY", {}).get("fragment"))
        fragments["PUZZLE_3_VERIFY"]    = frag
        puzzles_solved["PUZZLE_3_VERIFY"] = True
        print(f"  ✓ Fragment 3 = {frag}")
        if r.get("door_unlocked"):
            print(f"  ✓ Door unlocked: {r['door_unlocked']}")
        return True
    print(f"  ✗ Puzzle 3 failed: {r}")
    return False


def solve_puzzle4():
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
        puzzles_solved["PUZZLE_4_PASSCODE"] = True
        return (r.get("completion_token") or r.get("jwt") or r.get("token"))
    print(f"  ✗ Puzzle 4 failed: {r}")
    return None

# ── Discovery phase ───────────────────────────────────────
def run_discovery(all_rooms):
    """
    Visit every reachable room, collect items, craft.
    Keeps looping until no new rooms can be reached.
    (Same logic as JS runDiscovery)
    """
    visited = set()
    made_progress = True

    while made_progress:
        made_progress = False
        for room in all_rooms:
            if room in visited:
                continue
            if room == "CORE_CHAMBER":
                continue  # save for last

            if navigate_to(room):
                look_r = api_look()
                update_directions(current_room, look_r)
                scan_and_collect(look_r)
                craft_all()
                visited.add(room)
                made_progress = True
                print(f"  ✓ Visited {room} | inventory: {len(inventory)} items")

# ── Main ──────────────────────────────────────────────────
def solve():
    global current_room, actions_used

    print("=== The Signal — Automated Solver v2 (Hybrid) ===")
    print(f"Email: {EMAIL}\n")

    # 1. Start session
    print("[1] Starting session...")
    r = api_start()
    current_room = r.get("current_room", "ENTRANCE_HALL")
    actions_used = r.get("actions_used", 0)
    print(f"  Room: {current_room}")

    # 2. Load map
    print("\n[2] Loading map...")
    all_rooms = load_lock_info()

    # Learn directions from starting room
    look_r = api_look()
    update_directions(current_room, look_r)

    # 3. Improvement 3: Recover any already-solved fragments
    print("\n[3] Checking for existing progress...")
    recover_fragments()

    # 4. Main loop — up to 10 cycles (like JS version)
    print("\n[4] Starting solver cycles...")
    for cycle in range(10):
        print(f"\n{'─'*50}")
        print(f"  CYCLE {cycle + 1}/10")
        print(f"{'─'*50}")

        # Discovery — visit all rooms, collect items
        run_discovery(all_rooms)

        # Refresh lock info (doors may have unlocked)
        load_lock_info()

        # Try to solve puzzles
        print("\n  Solving puzzles...")
        if not puzzles_solved.get("PUZZLE_1_PIN"):
            solve_puzzle1()

        if not puzzles_solved.get("PUZZLE_2_FREQUENCY"):
            solve_puzzle2()

        if not puzzles_solved.get("PUZZLE_3_VERIFY"):
            solve_puzzle3()

        # Refresh lock info again after puzzle 3
        load_lock_info()
        # Re-learn CONTROL_ROOM exits (door to CORE_CHAMBER may now be open)
        if navigate_to("CONTROL_ROOM"):
            look_r = api_look()
            update_directions("CONTROL_ROOM", look_r)

        # Try final puzzle
        if all([
            puzzles_solved.get("PUZZLE_1_PIN"),
            puzzles_solved.get("PUZZLE_2_FREQUENCY"),
            puzzles_solved.get("PUZZLE_3_VERIFY"),
        ]):
            token = solve_puzzle4()
            if token:
                print(f"\nActions used: {actions_used}")
                print(f"\n{'='*60}")
                print("JWT TOKEN:")
                print(token)
                print("="*60)
                return

        print(f"\n  End of cycle {cycle+1}")
        print(f"  Fragments: {fragments}")
        print(f"  Inventory: {list(inventory.keys())}")

    print("\n❌ Could not solve after 10 cycles!")
    print(f"Fragments: {fragments}")
    print(f"Puzzles:   {puzzles_solved}")
    print(f"Inventory: {list(inventory.keys())}")
    print(f"Memory:    {list(memory.keys())}")


if __name__ == "__main__":
    solve()