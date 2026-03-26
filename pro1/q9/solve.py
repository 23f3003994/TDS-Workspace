
import requests
import statistics
import json
import os
from collections import deque
import math
BASE = "https://tds-network-games.sanand.workers.dev/labyrinth"
SESSION_TOKEN = 'cd5f8dc4-2521-46b0-806b-b2ab123a7539'
# 'd96673c6-91f5-412b-b7e9-84151daebede'
PROGRESS_FILE = "progress.json"
EXIT_ROOM = 120

HEADERS = {
    "Content-Type": "application/json",
    "X-Session-Token": SESSION_TOKEN
}

OPPOSITE = {"north":"south","south":"north","east":"west","west":"east"}

room_map        = {}
room_exits      = {}
visited         = set()
collected_rooms = set()
real_fragments  = []
clean_fragments = []
required_rooms  = []
current_room    = None

def save_progress():
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "room_map":        room_map,
            "room_exits":      {str(k): v for k,v in room_exits.items()},
            "visited":         list(visited),
            "collected_rooms": list(collected_rooms),
            "real_fragments":  real_fragments,
            "clean_fragments": clean_fragments,
            "required_rooms":  required_rooms,
            "optimal_path":    compute_optimal_path() or [],
        }, f, indent=2)
    print(f"  [saved] {len(visited)} rooms | real={len(real_fragments)} | "
          f"clean={len(clean_fragments)} | required_rooms={required_rooms}")

def load_progress():
    global room_map, room_exits, visited, collected_rooms
    global real_fragments, clean_fragments, required_rooms
    if not os.path.exists(PROGRESS_FILE):
        print("Starting fresh.")
        return False
    with open(PROGRESS_FILE) as f:
        d = json.load(f)
    room_map        = {int(k): v for k,v in d["room_map"].items()}
    room_exits      = {int(k): {dr: int(v) for dr,v in ex.items()}
                       for k,ex in d["room_exits"].items()}
    visited         = set(int(x) for x in d["visited"])
    collected_rooms = set(int(x) for x in d["collected_rooms"])
    real_fragments  = d.get("real_fragments", [])
    clean_fragments = d.get("clean_fragments", [])
    required_rooms  = d.get("required_rooms", [])
    opt             = d.get("optimal_path", [])
    print(f"Loaded: {len(visited)} rooms | real={len(real_fragments)} | clean={len(clean_fragments)}")
    print(f"  required_rooms  : {required_rooms}")
    print(f"  clean_fragments : {clean_fragments}")
    if opt:
        print(f"  optimal_path    : {len(opt)} moves")
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
    """
    Once all required_rooms are known, compute greedy shortest
    path: start -> nearest required -> ... -> all required -> room 120
    Returns list of directions to follow.
    """
    if not required_rooms or not room_exits:
        return []

    # need a start — use first required room as anchor
    # we compute pairwise distances between required_rooms + EXIT_ROOM
    targets = list(required_rooms) + [EXIT_ROOM]

    # greedy nearest neighbour from first required room
    # (we don't know start room ahead of time so we just order the targets)
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

    # build full direction path
    full_path = []
    for i in range(len(ordered) - 1):
        seg = find_path(ordered[i], ordered[i+1])
        if seg is None:
            print(f"  [path] No path from {ordered[i]} to {ordered[i+1]}")
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
    rms    = data.get("response_ms") if isinstance(data, dict) else None

    if ftype == "required":
        if room_id not in required_rooms:
            required_rooms.append(room_id)
        if rms is not None and not is_corrupt(rms):
            real_fragments.append(float(rms))
            if is_complete(data):
                clean_fragments.append(float(rms))
                print(f"    ✓ CLEAN | room={room_id} | response_ms={rms}")
            else:
                print(f"    ~ CORRUPT field | room={room_id} | response_ms={rms}")
        else:
            print(f"    ~ response_ms CORRUPT | room={room_id}")
    else:
        print(f"    ✗ distractor | room={room_id} | response_ms={rms}")
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
                print(f"  Room {new_room} | has_item={r.get('has_item')} | exits={r.get('exits')}")

                if r.get("has_item") and not r.get("item_collected"):
                    handle_collect(new_room)

                inv = inventory()
                print(f"  Fragments: {inv['fragments_collected']}/{inv['fragments_required']} | moves: {inv['moves_used']}")

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
    """
    Once all 12 required_rooms are known from progress.json,
    run optimal path in a fresh session to collect all + submit.
    """
    global current_room, real_fragments, clean_fragments
    # fresh session — clear old fragment values
    real_fragments.clear()
    clean_fragments.clear()
    collected_rooms.clear()  # ← clear this too!

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

        # Force collect — ignore collected_rooms cache
        # since session was cleared, server reset item_collected
        r = look()
        if r.get("has_item"):
            # temporarily remove from collected_rooms to force collection
            collected_rooms.discard(nearest)
            handle_collect(nearest)
        
        inv = inventory()
        print(f"  Fragments: {inv['fragments_collected']}/12 | moves: {inv['moves_used']}")
        unvisited.remove(nearest)

    inv = inventory()
    if inv["fragments_collected"] < inv["fragments_required"]:
        print(f"Only {inv['fragments_collected']}/12 collected!")
        return False

    return True

# ── Main ──────────────────────────────────────────────────
print("=== Data Labyrinth Solver ===")
load_progress()

# If we already know all 12 required rooms — do optimal run
if len(required_rooms) >= 12:
    print(f"\n=== OPTIMAL RUN (all {len(required_rooms)} required rooms known) ===")
    success = optimal_run()
else:
    print(f"\n=== EXPLORING (found {len(required_rooms)}/12 required rooms so far) ===")
    success = explore()

if success:
    print(f"\nClean fragments : {clean_fragments}")

    if len(clean_fragments) < 2:
        print("Not enough clean fragments!")
    else:
        # population std
        mean = sum(clean_fragments)/len(clean_fragments)
        pop_std = math.sqrt(sum((x-mean)**2 for x in clean_fragments)/len(clean_fragments))
        pop_cv  = pop_std/mean
        print(f"Mean={mean}  | CV={round(pop_cv)}")
        print(f"population CV: {pop_cv}")
    
        #if this doesnt work try submitting manually from the game page ,
        #ie once 12 fragments are collected go to game page,(F5 or resload) start with my email_id, all fragments collected in the current session will be shown
        #submit value there

        # mean = statistics.mean(clean_fragments)
        # std  = statistics.stdev(clean_fragments)
        # cv   = std / mean
        # print(f"Mean={mean} | Std={std} | CV={round(cv,4)}")

        print(f"\nNavigating to room {EXIT_ROOM}...")
        if navigate_to(EXIT_ROOM):
            print(f"Submitting {pop_cv}...")
            res = submit(pop_cv)
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