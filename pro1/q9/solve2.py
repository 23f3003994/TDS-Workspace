import requests
import json
import os
from collections import deque

BASE = "https://tds-network-games.sanand.workers.dev/labyrinth"
SESSION_TOKEN = '3dea306f-19de-4a65-b579-5ff9a8b35cdb'
PROGRESS_FILE = "progress2.json"
EXIT_ROOM = 120

HEADERS = {
    "Content-Type": "application/json",
    "X-Session-Token": SESSION_TOKEN
}

OPPOSITE = {"north":"south","south":"north","east":"west","west":"east"}

room_map                = {}
room_exits              = {}
visited                 = set()
collected_rooms         = set()
required_fragments_data = []  # ALL required rows
clean_fragments_data    = []  # only complete rows (for calculation)
required_rooms          = []
current_room            = None

def save_progress():
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "room_map":                room_map,
            "room_exits":              {str(k): v for k,v in room_exits.items()},
            "visited":                 list(visited),
            "collected_rooms":         list(collected_rooms),
            "required_fragments_data": required_fragments_data,
            "clean_fragments_data":    clean_fragments_data,
            "required_rooms":          required_rooms,
            "optimal_path":            compute_optimal_path() or [],
        }, f, indent=2)
    print(f"  [saved] {len(visited)} rooms | "
          f"required={len(required_fragments_data)} | "
          f"clean={len(clean_fragments_data)} | "
          f"required_rooms={required_rooms}")

def load_progress():
    global room_map, room_exits, visited, collected_rooms
    global required_fragments_data, clean_fragments_data, required_rooms
    if not os.path.exists(PROGRESS_FILE):
        print("Starting fresh.")
        return False
    with open(PROGRESS_FILE) as f:
        d = json.load(f)
    room_map                = {int(k): v for k,v in d["room_map"].items()}
    room_exits              = {int(k): {dr: int(v) for dr,v in ex.items()}
                               for k,ex in d["room_exits"].items()}
    visited                 = set(int(x) for x in d["visited"])
    collected_rooms         = set(int(x) for x in d["collected_rooms"])
    required_fragments_data = d.get("required_fragments_data", [])
    clean_fragments_data    = d.get("clean_fragments_data", [])
    required_rooms          = d.get("required_rooms", [])
    opt                     = d.get("optimal_path", [])
    print(f"Loaded: {len(visited)} rooms | "
          f"required={len(required_fragments_data)} | "
          f"clean={len(clean_fragments_data)}")
    print(f"  required_rooms      : {required_rooms}")
    print(f"  clean_fragments_data: {clean_fragments_data}")
    if opt:
        print(f"  optimal_path        : {len(opt)} moves")
    return True

def is_corrupt(v):
    return str(v).upper() == "CORRUPT"

def is_complete(data):
    if not isinstance(data, dict):
        return False
    return all(v is not None and not is_corrupt(v) for v in data.values())

# ── API ───────────────────────────────────────────────────
def look():
    return requests.get(f"{BASE}/look", headers=HEADERS).json()

def move(direction):
    return requests.post(f"{BASE}/move", headers=HEADERS,
                         json={"direction": direction}).json()

def collect():
    return requests.post(f"{BASE}/collect", headers=HEADERS).json()

def inventory():
    return requests.get(f"{BASE}/inventory", headers=HEADERS).json()

def submit(answer):
    return requests.post(f"{BASE}/submit", headers=HEADERS,
                         json={"answer": str(answer)}).json()

# ── Navigation ────────────────────────────────────────────
def go(direction):
    global current_room
    r = move(direction)
    if "room_id" not in r:
        print(f"  [failed]: {r}")
        return None
    current_room = r["room_id"]
    return r

def find_path(start, goal):
    if start == goal:
        return []
    queue = deque([(start, [])])
    seen  = {start}
    while queue:
        node, path = queue.popleft()
        for d, nb in room_exits.get(node, {}).items():
            if nb in seen:
                continue
            np = path + [d]
            if nb == goal:
                return np
            seen.add(nb)
            queue.append((nb, np))
    return None

def navigate_to(target):
    global current_room
    if current_room == target:
        return True
    path = find_path(current_room, target)
    if not path:
        return False
    for d in path:
        if not go(d):
            return False
    return True

def compute_optimal_path():
    if not required_rooms or not room_exits:
        return []
    unvisited = list(required_rooms)
    ordered   = []
    current   = unvisited[0]
    ordered.append(current)
    unvisited.remove(current)
    while unvisited:
        nearest = min(unvisited,
                      key=lambda r: len(find_path(current, r) or [999]))
        ordered.append(nearest)
        unvisited.remove(nearest)
        current = nearest
    ordered.append(EXIT_ROOM)
    print(f"  Optimal visit order: {ordered}")
    full_path = []
    for i in range(len(ordered) - 1):
        seg = find_path(ordered[i], ordered[i+1])
        if seg is None:
            return []
        full_path.extend(seg)
    return full_path

# ── Collection ────────────────────────────────────────────
def handle_collect(room_id):
    if room_id in collected_rooms:
        return
    collected_rooms.add(room_id)
    result = collect()
    ftype  = result.get("fragment_type", "unknown")
    frag   = result.get("fragment", {})
    data   = frag.get("data") if isinstance(frag.get("data"), dict) else frag

    if ftype == "required":
        if room_id not in required_rooms:
            required_rooms.append(room_id)
        # save ALL required rows
        required_fragments_data.append(data)
        # save only clean ones for calculation
        if is_complete(data):
            clean_fragments_data.append(data)
            print(f"    ✓ CLEAN | room={room_id} | "
                  f"error_code={data.get('error_code')}")
        else:
            print(f"    ~ CORRUPT | room={room_id} | data={data}")
    else:
        print(f"    ✗ distractor | room={room_id}")
    save_progress()

# ── BFS Explore ───────────────────────────────────────────
def explore():
    global current_room
    room = look()
    current_room = room["room_id"]
    print(f"Current room: {current_room}")

    if current_room not in visited:
        visited.add(current_room)
        room_map[current_room]   = room["exits"]
        room_exits[current_room] = {}

    if room.get("has_item") and not room.get("item_collected"):
        handle_collect(current_room)

    queue = deque(rid for rid in visited
                  if set(room_exits.get(rid,{}).keys()) < set(room_map.get(rid,[])))
    if current_room not in queue:
        queue.appendleft(current_room)

    print(f"Rooms with unexplored exits: {len(queue)}")

    while queue:
        from_room = queue.popleft()
        if not navigate_to(from_room):
            continue

        for direction in room_map.get(from_room, []):
            if direction in room_exits.get(from_room, {}):
                continue

            r = go(direction)
            if not r:
                continue

            new_room = r["room_id"]
            room_exits.setdefault(from_room, {})[direction]            = new_room
            room_exits.setdefault(new_room,   {})[OPPOSITE[direction]] = from_room

            if new_room not in visited:
                visited.add(new_room)
                room_map[new_room] = r.get("exits", [])
                print(f"  Room {new_room} | "
                      f"has_item={r.get('has_item')} | "
                      f"exits={r.get('exits')}")

                if r.get("has_item") and not r.get("item_collected"):
                    handle_collect(new_room)

                inv = inventory()
                print(f"  Fragments: {inv['fragments_collected']}/"
                      f"{inv['fragments_required']} | "
                      f"moves: {inv['moves_used']}")

                if inv["fragments_collected"] >= inv["fragments_required"]:
                    print("\nAll 12 collected!")
                    save_progress()
                    return True

                queue.append(new_room)
                save_progress()

            navigate_to(from_room)

    save_progress()
    return False

# ── Optimal Run ───────────────────────────────────────────
def optimal_run():
    global current_room, required_fragments_data, clean_fragments_data
    required_fragments_data.clear()
    clean_fragments_data.clear()
    collected_rooms.clear()

    print(f"\nRequired rooms to visit: {required_rooms}")
    room = look()
    current_room = room["room_id"]
    print(f"Starting from room {current_room}")

    unvisited = list(required_rooms)
    while unvisited:
        nearest = min(unvisited,
                      key=lambda r: len(find_path(current_room, r) or [999]*999))
        print(f"  Navigating to required room {nearest}...")
        if not navigate_to(nearest):
            print(f"  Cannot reach {nearest}!")
            return False

        r = look()
        if r.get("has_item"):
            collected_rooms.discard(nearest)
            handle_collect(nearest)

        inv = inventory()
        print(f"  Fragments: {inv['fragments_collected']}/12 | "
              f"moves: {inv['moves_used']}")
        unvisited.remove(nearest)

    inv = inventory()
    if inv["fragments_collected"] < inv["fragments_required"]:
        print(f"Only {inv['fragments_collected']}/12 collected!")
        return False
    return True

# ── Answer Calculation ────────────────────────────────────
def compute_answer():
    """Q4: count records where error_code > 75th percentile of error_code"""
    if not clean_fragments_data:
        print("No clean fragments!")
        return None

    error_codes = []
    for row in clean_fragments_data:
        ec = row.get("error_code")
        if ec is not None and not is_corrupt(ec):
            error_codes.append(float(ec))

    if not error_codes:
        print("No valid error_code values!")
        return None

    print(f"\nAll error_codes : {error_codes}")

    # 75th percentile using linear interpolation
    error_codes_sorted = sorted(error_codes)
    n       = len(error_codes_sorted)
    p75_idx = 0.75 * (n - 1)
    lower   = int(p75_idx)
    upper   = min(lower + 1, n - 1)
    frac    = p75_idx - lower
    p75     = (error_codes_sorted[lower] +
               frac * (error_codes_sorted[upper] - error_codes_sorted[lower]))

    count = sum(1 for ec in error_codes if ec > p75)

    print(f"75th percentile : {p75}")
    print(f"count > p75     : {count}")
    return count

# ── Main ──────────────────────────────────────────────────
print("=== Data Labyrinth Solver ===")
load_progress()

if len(required_rooms) >= 12:
    print(f"\n=== OPTIMAL RUN ===")
    success = optimal_run()
else:
    print(f"\n=== EXPLORING ({len(required_rooms)}/12 required rooms known) ===")
    success = explore()

if success:
    answer = compute_answer()
    if answer is not None:
        print(f"\nNavigating to room {EXIT_ROOM}...")
        if navigate_to(EXIT_ROOM):
            print(f"Submitting {answer}...")
            res = submit(answer)
            print(f"Response: {res}")
            token = (res.get("completion_token") or res.get("jwt") or
                     res.get("token") or res.get("jwt_token"))
            if token:
                print(f"\n{'='*50}")
                print("YOUR JWT TOKEN:")
                print(token)
                print('='*50)
            else:
                print("No token — check response above")
        else:
            print("Cannot reach room 120!")
else:
    print(f"\nNot all 12 collected yet.")
    print(f"Known required rooms ({len(required_rooms)}/12): {required_rooms}")
    opt = compute_optimal_path()
    if opt:
        print(f"Optimal path when ready: {len(opt)} moves")
    print("\nClear session and rerun to continue.")