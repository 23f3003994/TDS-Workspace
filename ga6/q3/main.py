
"""
Multi-Model Robustness Audit — Full Optimizer
==============================================
Finds the shortest prompt (minimum total Word Count) achieving:
  - Macro-Mean  >= 97%   (sigmoid-based mean accuracy across 4 LLMs)
  - Model Floor >= 92%   (worst single model must be >= 92%)

SCORING FORMULA (from validator source):
  logit(model) = baseline[model] + sum(selected sensitivities) + sum(pair bonuses)
  score(model) = sigmoid(logit)  =  1 / (1 + e^(-logit))
  Macro-Mean   = mean of 4 model scores
  Model Floor  = min  of 4 model scores
"""

import math
from itertools import combinations

# ─── Sigmoid ──────────────────────────────────────────────────────────────────
def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

# ─── Instructions: {ID: {wc, scores={model: sensitivity}}} ───────────────────
instructions = {
    'I1':  {'wc': 13, 'scores': {'gpt-4o':  0.20, 'gpt-4.1':  1.34, 'gpt-4.1-mini':  0.25, 'gpt-5-mini':  0.09}},
    'I2':  {'wc': 17, 'scores': {'gpt-4o': -0.02, 'gpt-4.1': -0.03, 'gpt-4.1-mini':  1.16, 'gpt-5-mini': -0.15}},
    'I3':  {'wc': 16, 'scores': {'gpt-4o':  1.10, 'gpt-4.1':  1.31, 'gpt-4.1-mini': -0.36, 'gpt-5-mini':  0.79}},
    'I4':  {'wc': 15, 'scores': {'gpt-4o': -0.16, 'gpt-4.1':  1.39, 'gpt-4.1-mini':  1.39, 'gpt-5-mini': -0.94}},
    'I5':  {'wc':  5, 'scores': {'gpt-4o':  0.67, 'gpt-4.1':  0.22, 'gpt-4.1-mini':  0.84, 'gpt-5-mini':  0.39}},
    'I6':  {'wc':  5, 'scores': {'gpt-4o':  1.21, 'gpt-4.1':  0.47, 'gpt-4.1-mini':  0.26, 'gpt-5-mini': -0.31}},
    'I7':  {'wc':  8, 'scores': {'gpt-4o':  0.00, 'gpt-4.1':  1.34, 'gpt-4.1-mini': -0.14, 'gpt-5-mini':  0.34}},
    'I8':  {'wc': 15, 'scores': {'gpt-4o':  1.25, 'gpt-4.1':  0.43, 'gpt-4.1-mini':  0.47, 'gpt-5-mini':  0.37}},
    'I9':  {'wc': 11, 'scores': {'gpt-4o': -0.34, 'gpt-4.1':  1.17, 'gpt-4.1-mini': -0.04, 'gpt-5-mini':  1.31}},
    'I10': {'wc':  7, 'scores': {'gpt-4o':  0.95, 'gpt-4.1':  1.15, 'gpt-4.1-mini':  0.94, 'gpt-5-mini': -0.27}},
    'I11': {'wc': 12, 'scores': {'gpt-4o':  1.01, 'gpt-4.1':  0.43, 'gpt-4.1-mini':  1.21, 'gpt-5-mini': -0.38}},
    'I12': {'wc':  5, 'scores': {'gpt-4o':  0.14, 'gpt-4.1': -0.11, 'gpt-4.1-mini':  1.39, 'gpt-5-mini': -0.27}},
    'I13': {'wc':  5, 'scores': {'gpt-4o':  1.09, 'gpt-4.1': -0.20, 'gpt-4.1-mini':  0.45, 'gpt-5-mini':  0.36}},
    'I14': {'wc': 11, 'scores': {'gpt-4o': -0.01, 'gpt-4.1':  1.07, 'gpt-4.1-mini':  0.39, 'gpt-5-mini':  0.19}},
    'I15': {'wc':  9, 'scores': {'gpt-4o': -0.28, 'gpt-4.1':  1.06, 'gpt-4.1-mini':  1.19, 'gpt-5-mini':  0.87}},
    'I16': {'wc':  9, 'scores': {'gpt-4o':  0.27, 'gpt-4.1':  1.26, 'gpt-4.1-mini':  1.01, 'gpt-5-mini':  1.13}},
    'I17': {'wc': 15, 'scores': {'gpt-4o': -0.32, 'gpt-4.1': -0.36, 'gpt-4.1-mini':  0.88, 'gpt-5-mini':  1.36}},
    'I18': {'wc': 10, 'scores': {'gpt-4o': -0.09, 'gpt-4.1': -0.01, 'gpt-4.1-mini':  1.85, 'gpt-5-mini': -0.34}},
    'I19': {'wc':  5, 'scores': {'gpt-4o':  0.98, 'gpt-4.1':  0.34, 'gpt-4.1-mini':  1.12, 'gpt-5-mini':  1.38}},
    'I20': {'wc': 13, 'scores': {'gpt-4o':  1.02, 'gpt-4.1':  0.50, 'gpt-4.1-mini':  0.17, 'gpt-5-mini':  1.20}},
    'I21': {'wc': 13, 'scores': {'gpt-4o':  1.10, 'gpt-4.1':  0.36, 'gpt-4.1-mini':  1.28, 'gpt-5-mini':  0.26}},
}

# ─── Pair Bonuses (added to every model's logit when both IDs are selected) ───
pair_bonuses_raw = {
    ('I5', 'I17'): -0.15, ('I6', 'I15'):  0.50, ('I8', 'I21'): -0.35,
    ('I1', 'I8'):  -0.23, ('I8', 'I19'): -0.50, ('I4', 'I7'):   0.68,
    ('I8', 'I20'):  0.03, ('I6', 'I10'): -0.16, ('I8', 'I17'): -0.40,
    ('I12','I14'):  0.60, ('I3', 'I12'):  0.04, ('I1', 'I11'):  0.50,
    ('I2', 'I7'):   0.54, ('I17','I20'): -0.06, ('I9', 'I20'): -0.48,
    ('I13','I16'): -0.67, ('I5', 'I20'): -0.70, ('I11','I19'):  0.57,
    ('I4', 'I11'):  0.46, ('I18','I19'):  0.12, ('I17','I19'):  0.06,
    ('I11','I14'):  0.55, ('I17','I18'):  0.24, ('I2', 'I17'):  0.65,
    ('I4', 'I14'):  0.29, ('I5', 'I13'): -0.44, ('I2', 'I12'): -0.31,
    ('I6', 'I19'):  0.14, ('I3', 'I10'):  0.06, ('I1', 'I3'):  -0.46,
    ('I4', 'I15'):  0.57, ('I5', 'I10'): -0.08, ('I3', 'I19'): -0.44,
    ('I8', 'I12'):  0.30, ('I7', 'I12'):  0.02, ('I5', 'I9'):   0.66,
    ('I1', 'I18'):  0.65, ('I9', 'I14'): -0.51, ('I4', 'I19'):  0.01,
    ('I2', 'I6'):  -0.20, ('I5', 'I6'):  -0.58, ('I14','I19'): -0.47,
}
pair_bonuses = {frozenset(k): v for k, v in pair_bonuses_raw.items()}

# ─── Model Baselines ──────────────────────────────────────────────────────────
baselines = {
    'gpt-4o':       -1.54,
    'gpt-4.1':      -1.20,
    'gpt-4.1-mini': -2.95,
    'gpt-5-mini':   -0.29,
}
models = ['gpt-4o', 'gpt-4.1', 'gpt-4.1-mini', 'gpt-5-mini']

# ─── Thresholds ───────────────────────────────────────────────────────────────
MEAN_TARGET  = 0.97   # Macro-Mean  >= 97%
FLOOR_TARGET = 0.92   # Model Floor >= 92%


# ─── Evaluation Function ──────────────────────────────────────────────────────
def evaluate(subset):
    """
    Given a list/tuple of instruction IDs, compute:
      - mean_acc  : sigmoid-based macro-mean across 4 models
      - floor_acc : worst single model score
      - wc        : total word count
      - accs      : list of per-model accuracy scores
    """
    ids = list(subset)

    # Sum all applicable pair bonuses (global, added to every model's logit)
    pair_bonus_total = 0.0
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pair_bonus_total += pair_bonuses.get(frozenset([ids[i], ids[j]]), 0.0)

    # Compute sigmoid score for each model
    accs = []
    for m in models:
        logit = baselines[m] + pair_bonus_total + sum(instructions[iid]['scores'][m] for iid in ids)
        accs.append(sigmoid(logit))

    mean_acc  = sum(accs) / 4
    floor_acc = min(accs)
    wc        = sum(instructions[i]['wc'] for i in ids)

    return mean_acc, floor_acc, wc, accs


# ─── Exhaustive Search ────────────────────────────────────────────────────────
def find_optimal():
    all_ids    = list(instructions.keys())
    best_wc    = float('inf')
    best_mean  = 0.0
    best_result = None

    print("Searching all subsets for minimum WC solution...\n")

    for size in range(1, len(all_ids) + 1):
        for combo in combinations(all_ids, size):
            # Fast WC pre-check before full evaluation
            wc = sum(instructions[i]['wc'] for i in combo)
            if wc > best_wc:
                continue

            mean_acc, floor_acc, wc, accs = evaluate(combo)

            if mean_acc >= MEAN_TARGET and floor_acc >= FLOOR_TARGET:
                if wc < best_wc or (wc == best_wc and mean_acc > best_mean + 1e-4):
                    best_wc    = wc
                    best_mean  = mean_acc
                    best_result = (wc, list(combo), mean_acc, floor_acc, accs)

    return best_result


# ─── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = find_optimal()

    if not result:
        print("No valid solution found.")
    else:
        wc, combo, mean_acc, floor_acc, accs = result
        ids_sorted = sorted(combo, key=lambda x: int(x[1:]))
        ids_str    = ','.join(ids_sorted)

        # Fragment labels for readability
        fragments = {
            'I1':'Step-by-step.',    'I2':'Act as Expert.',   'I3':'JSON Output.',
            'I4':'No yapping.',      'I5':'Few-shot (3).',     'I6':'Chain of Thought.',
            'I7':'Explain reasoning.','I8':'Professional tone.','I9':'Strict format.',
            'I10':'Avoid jargon.',   'I11':'Summary first.',  'I12':'Double check.',
            'I13':'Self-reflect.',   'I14':'Contextualize.',  'I15':'Verify logic.',
            'I16':'Brevity.',        'I17':'Analogies.',      'I18':'Citations.',
            'I19':'Persona: Mentor.','I20':'Persona: Auditor.','I21':'JSON schema.',
        }

        print("=" * 60)
        print("  OPTIMAL SOLUTION")
        print("=" * 60)
        print(f"  IDs selected : {ids_str}")
        print(f"  Fragments    :")
        for iid in ids_sorted:
            print(f"    {iid:4s} (WC={instructions[iid]['wc']:2d})  {fragments[iid]}")
        print(f"\n  Total WC     : {wc}")
        print(f"  Macro-Mean   : {mean_acc * 100:.4f}%  (threshold >= {MEAN_TARGET*100:.0f}%)")
        print(f"  Model Floor  : {floor_acc * 100:.4f}%  (threshold >= {FLOOR_TARGET*100:.0f}%)")
        print(f"\n  Per-model breakdown:")
        for m, a in zip(models, accs):
            marker = " <- floor" if a == floor_acc else ""
            print(f"    {m:18s}: {a * 100:.4f}%{marker}")

        # Exact submission string (4 decimal places matches validator tolerance of 5e-4)
        mean_str  = f"{round(mean_acc  * 100, 4)}"
        floor_str = f"{round(floor_acc * 100, 4)}"

        print(f"\n{'=' * 60}")
        print(f"  SUBMIT THIS EXACTLY:")
        print(f"  {ids_str}; {wc}; {mean_str}; {floor_str}")
        print(f"{'=' * 60}")