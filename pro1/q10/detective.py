"""
Graph Detective Solver
======================
Finds the compromised node in a 120-node financial transaction network.
Uses progress.json to survive session resets (like the Labyrinth solver).

Usage:
  1. Go to the game site, enter your email, click Start
  2. Open browser console, get session token:
       Object.entries(sessionStorage).map(([k,v]) => k+': '+v).join('\n')
  3. Paste token into SESSION_TOKEN below
  4. Run: python3 detective.py

To clear/reset session (if needed):
  fetch('https://tds-network-games.sanand.workers.dev/detective/clear', {
    method: 'POST',
    headers: {
    'Content-Type': 'application/json',
    'X-Session-Token': '085a3bf7-6de6-4b0d-a542-79f742d3483e'
  },
    body: JSON.stringify({email: '23f3003994@ds.study.iitm.ac.in', week: '2026-W13'})
  }).then(r => r.json()).then(console.log)


  to start again
  fetch('https://tds-network-games.sanand.workers.dev/detective/start', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email: '23f3003994@ds.study.iitm.ac.in'})
}).then(r => r.json()).then(console.log)

"""

import requests
import json
import os
from collections import deque

# ── CONFIG — update SESSION_TOKEN each new session ────────
BASE          = "https://tds-network-games.sanand.workers.dev/detective"
SESSION_TOKEN = "6f66b3c7-1549-4a19-afb9-2f37b9393156"   # <-- paste current token
EMAIL         = "23f3003994@ds.study.iitm.ac.in"
WEEK          = "2026-W13"
PROGRESS_FILE = "detective_progress.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Session-Token": SESSION_TOKEN
}

# ── State ─────────────────────────────────────────────────
graph   = {}    # node_id (int) -> {"attributes": {...}, "neighbors": [...], "degree": N}
degrees = {}    # node_id (int) -> degree  (free from neighbor_degrees!)
queried = set() # nodes we've already spent a query on
compromised_node = None
proof_path       = []

# ── Progress file ─────────────────────────────────────────
def save_progress():
    with open(PROGRESS_FILE, "w") as f:
        json.dump({
            "graph":            {str(k): v for k, v in graph.items()},
            "degrees":          {str(k): v for k, v in degrees.items()},
            "queried":          list(queried),
            "compromised_node": compromised_node,
            "proof_path":       proof_path,
        }, f, indent=2)
    print(f"  [saved] queried={len(queried)} | known_nodes={len(graph)} | "
          f"degrees_known={len(degrees)} | compromised={compromised_node}")

def load_progress():
    global graph, degrees, queried, compromised_node, proof_path
    if not os.path.exists(PROGRESS_FILE):
        print("No progress file found — starting fresh.")
        return False
    with open(PROGRESS_FILE) as f:
        d = json.load(f)
    graph            = {int(k): v for k, v in d.get("graph", {}).items()}
    degrees          = {int(k): v for k, v in d.get("degrees", {}).items()}
    queried          = set(int(x) for x in d.get("queried", []))
    compromised_node = d.get("compromised_node")
    proof_path       = d.get("proof_path", [])
    print(f"Loaded progress: queried={len(queried)} | known_nodes={len(graph)} | "
          f"degrees_known={len(degrees)} | compromised={compromised_node}")
    return True

# ── API calls ─────────────────────────────────────────────
def start_session():
    """Get anchor node info (free — no query used)."""
    r = requests.post(f"{BASE}/start",
                      headers=HEADERS,
                      json={"email": EMAIL})
    return r.json()

def query_node(node_id):
    """Query a node — costs 1 query. Returns data or None."""
    if node_id in queried:
        return graph.get(node_id)

    r = requests.get(f"{BASE}/node/{node_id}", headers=HEADERS)
    data = r.json()

    if "error" in data or "attributes" not in data:
        print(f"  [error] node {node_id}: {data}")
        return None

    queried.add(node_id)

    # Store full node data
    graph[node_id] = {
        "attributes": data["attributes"],
        "neighbors":  data["neighbors"],
        "degree":     data["degree"],
    }
    degrees[node_id] = data["degree"]

    # Free info: record ALL neighbor degrees
    for nb_str, deg in data.get("neighbor_degrees", {}).items():
        nb = int(nb_str)
        degrees[nb] = deg
        if nb not in graph:
            graph[nb] = graph.get(nb) or {"attributes": None, "neighbors": [], "degree": deg}

    attrs = data["attributes"]
    print(f"  Node {node_id:3d} | degree={data['degree']:2d} | "
          f"avg_tx_size={attrs['avg_tx_size']:6} | "
          f"tx_count={attrs['tx_count_daily']:3} | "
          f"tx_volume={attrs['tx_volume_daily']:6} | "
          f"remaining={data['queries_remaining']}")
    return graph[node_id]

def submit_answer(node_id, path):
    r = requests.post(f"{BASE}/submit",
                      headers=HEADERS,
                      json={"compromised_node": node_id, "path": path})
    return r.json()

# ── Suspicion scoring ─────────────────────────────────────
def suspicion_score(node_id):
    """
    Score based on the 3 clues:
    - Very high avg_tx_size  (transactions individually massive)
    - Very low tx_count_daily (transactions rare)
    - High tx_volume despite low count (concentrated funnel)
    """
    data = graph.get(node_id)
    if not data or not data.get("attributes"):
        return -1
    attrs = data["attributes"]

    avg_tx  = attrs.get("avg_tx_size",        0) or 0
    tx_cnt  = attrs.get("tx_count_daily",      1) or 1
    tx_vol  = attrs.get("tx_volume_daily",     0) or 0
    cp      = attrs.get("counterparty_count",  1) or 1

    # Main signal: massive transactions + rare count
    score = (avg_tx / 100.0)                  # huge avg_tx = very suspicious
    score += (tx_vol / tx_cnt) / 100.0        # high per-tx volume
    score += 50.0 / tx_cnt                    # penalise high counts
    score += 20.0 / cp                        # concentrated counterparties

    return score

# ── BFS shortest path ─────────────────────────────────────
def find_path(start, goal):
    """BFS through known graph to find shortest path (list of node IDs)."""
    if start == goal:
        return [start]
    queue = deque([(start, [start])])
    seen  = {start}
    while queue:
        node, path = queue.popleft()
        for nb in graph.get(node, {}).get("neighbors", []):
            if nb in seen:
                continue
            new_path = path + [nb]
            if nb == goal:
                return new_path
            seen.add(nb)
            queue.append((nb, new_path))
    return None

# ── Main solver ───────────────────────────────────────────
def solve():
    global compromised_node, proof_path

    load_progress()

    # ── Phase 0: If already solved, just submit ────────────
    if compromised_node and proof_path:
        print(f"\nAlready identified node {compromised_node}, path={proof_path}")
        print("Submitting...")
        result = submit_answer(compromised_node, proof_path)
        handle_result(result)
        return

    # ── Phase 1: Anchor node (free) ────────────────────────
    print("\n[Phase 1] Getting anchor node (free)...")
    start_data = start_session()

    if "anchor_node" not in start_data:
        print(f"Unexpected start response: {start_data}")
        return

    anchor = start_data["anchor_node"]
    anchor_id = anchor["id"]  # should be 1

    # Store anchor in graph (free — no query used)
    graph[anchor_id] = {
        "attributes": anchor["attributes"],
        "neighbors":  anchor["neighbors"],
        "degree":     anchor["degree"],
    }
    degrees[anchor_id] = anchor["degree"]

    print(f"Anchor node {anchor_id}: degree={anchor['degree']}, "
          f"avg_tx_size={anchor['attributes']['avg_tx_size']}, "
          f"tx_count={anchor['attributes']['tx_count_daily']}")
    print(f"Anchor neighbors ({len(anchor['neighbors'])}): {anchor['neighbors']}")

    # ── Phase 2: Query anchor's neighbours ─────────────────
    print(f"\n[Phase 2] Querying anchor neighbours ({len(anchor['neighbors'])} nodes)...")
    for nb in anchor["neighbors"]:
        if nb in queried:
            continue
        if len(queried) >= 40:
            print("  [budget] Stopping phase 2 at 40 queries")
            break
        query_node(nb)
        save_progress()

    # ── Phase 3: Score ALL known nodes ─────────────────────
    print(f"\n[Phase 3] Scoring all {len(graph)} known nodes...")
    scores = {}
    for node_id in graph:
        if graph[node_id].get("attributes"):
            scores[node_id] = suspicion_score(node_id)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    print("\nTop 15 most suspicious queried nodes:")
    print(f"  {'Node':>5} | {'Score':>8} | {'avg_tx_size':>12} | {'tx_count':>8} | {'tx_volume':>10} | {'cp_count':>8}")
    print("  " + "-"*65)
    shown = 0
    for node_id, score in ranked:
        if not graph[node_id].get("attributes"):
            continue
        attrs = graph[node_id]["attributes"]
        print(f"  {node_id:5d} | {score:8.1f} | {attrs['avg_tx_size']:12} | "
              f"{attrs['tx_count_daily']:8} | {attrs['tx_volume_daily']:10} | "
              f"{attrs['counterparty_count']:8}")
        shown += 1
        if shown >= 15:
            break

    # ── Phase 4: Query suspicious UNQUERIED nodes ──────────
    # Use degree info to find low-degree peripheral nodes we haven't queried yet
    unqueried_nodes = [n for n in graph if n not in queried]
    unqueried_by_degree = sorted(unqueried_nodes, key=lambda n: degrees.get(n, 999))

    print(f"\n[Phase 4] Querying {min(12, len(unqueried_by_degree))} low-degree unqueried nodes...")
    print(f"  (Budget remaining: {55 - len(queried)} queries)")

    for node_id in unqueried_by_degree:
        if len(queried) >= 52:
            print("  [budget] Stopping at 52 queries")
            break
        data = query_node(node_id)
        if data and data.get("attributes"):
            scores[node_id] = suspicion_score(node_id)
        save_progress()

    # ── Phase 5: Final ranking ─────────────────────────────
    print("\n[Phase 5] Final ranking of all scored nodes...")
    final_ranked = sorted(
        [(n, s) for n, s in scores.items() if graph[n].get("attributes")],
        key=lambda x: x[1], reverse=True
    )

    print("\nTop 10 suspects (FINAL):")
    print(f"  {'Node':>5} | {'Score':>8} | {'avg_tx_size':>12} | {'tx_count':>8} | {'tx_volume':>10}")
    print("  " + "-"*55)
    for node_id, score in final_ranked[:10]:
        attrs = graph[node_id]["attributes"]
        marker = " <<< SUSPECT" if node_id == final_ranked[0][0] else ""
        print(f"  {node_id:5d} | {score:8.1f} | {attrs['avg_tx_size']:12} | "
              f"{attrs['tx_count_daily']:8} | {attrs['tx_volume_daily']:10}{marker}")

    # The top scorer is our compromised node
    compromised_node = final_ranked[0][0]
    comp_attrs = graph[compromised_node]["attributes"]
    print(f"\n>>> COMPROMISED NODE: {compromised_node}")
    print(f"    avg_tx_size  = {comp_attrs['avg_tx_size']}")
    print(f"    tx_count     = {comp_attrs['tx_count_daily']}")
    print(f"    tx_volume    = {comp_attrs['tx_volume_daily']}")
    print(f"    in_out_ratio = {comp_attrs['in_out_ratio']}")
    print(f"    counterparty = {comp_attrs['counterparty_count']}")

    # ── Phase 6: Find shortest path ────────────────────────
    print(f"\n[Phase 6] Finding shortest path from {anchor_id} to {compromised_node}...")
    proof_path = find_path(anchor_id, compromised_node)

    if proof_path:
        print(f"Path found ({len(proof_path)-1} hops): {proof_path}")
    else:
        print("No direct path found — querying compromised node's neighbors to bridge gap...")
        comp_neighbors = graph[compromised_node].get("neighbors", [])
        for nb in comp_neighbors[:5]:
            if nb not in queried and len(queried) < 54:
                query_node(nb)
        proof_path = find_path(anchor_id, compromised_node)
        if proof_path:
            print(f"Path found after bridging ({len(proof_path)-1} hops): {proof_path}")
        else:
            print("Still no path! The graph may be disconnected in known data.")
            print(f"Known neighbors of {compromised_node}: {graph[compromised_node].get('neighbors', [])}")
            save_progress()
            return

    save_progress()

    # ── Phase 7: Submit ────────────────────────────────────
    print(f"\n[Phase 7] Submitting: node={compromised_node}, path={proof_path}")
    result = submit_answer(compromised_node, proof_path)
    handle_result(result)


def handle_result(result):
    print(f"\nSubmission response: {result}")

    token = (result.get("completion_token") or
             result.get("jwt") or
             result.get("token") or
             result.get("jwt_token"))

    if token:
        print(f"\n{'='*60}")
        print("YOUR JWT TOKEN (copy this into the answer box):")
        print(token)
        print('='*60)
    else:
        # Check if wrong answer
        if result.get("correct") is False or "incorrect" in str(result).lower():
            print("\n[WRONG] Node or path was incorrect.")
            print("Try the 2nd or 3rd ranked suspect from the list above.")
            print("Update compromised_node in detective_progress.json and rerun.")
        else:
            print("\nNo token in response. Full response shown above.")
            print("If the game shows a token on screen, copy it from there.")


if __name__ == "__main__":
    print("=== Graph Detective Solver ===")
    print(f"Email: {EMAIL} | Week: {WEEK}")
    print(f"Session token: {SESSION_TOKEN[:8]}...")
    print()
    solve()