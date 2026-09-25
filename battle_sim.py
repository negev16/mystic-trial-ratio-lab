"""
Mystic Trial Ratio Lab - Python battle engine.

Same model as the web calculator (index.html), for testing and analysis.
No dependencies: runs on plain Python 3.8+.

    python battle_sim.py            # runs the built-in example
    python battle_sim.py --runs 1000

Model (community reverse-engineered, not official):
    attack  = base_atk * (1+Atk%) * 10 * (1+Leth%) / 100
    defense = 10 * (1+Def%) * base_hp * (1+HP%) / 100
    army    = sqrt(squad_troops * min(total_A, total_B))
    kills   = army * attack / target_defense * counter(1.10) / 100
Targets: first living enemy line (Inf -> Cav -> Arc). Cavalry skip to archers
20% of rounds, archers fire twice 10% of rounds. Both sides hit simultaneously.
"""
import argparse
import math
import random

# [inf_atk, inf_hp, cav_atk, cav_hp, arc_atk, arc_hp]; base Leth = base Def = 10
BASE = {
    "T6": [243, 730, 730, 243, 974, 183],
    "T9": [400, 1200, 1200, 400, 1600, 300],
    "T10": [472, 1416, 1416, 472, 1888, 354],
    "T10.1": [491, 1473, 1473, 491, 1964, 368],
    "T10.2": [515, 1546, 1546, 515, 2062, 387],
    "T10.3": [541, 1624, 1624, 541, 2165, 406],
    "T10.4": [568, 1705, 1705, 568, 2273, 426],
    "T10.5": [597, 1790, 1790, 597, 2387, 448],
    "T11": [566, 1699, 1699, 566, 2266, 390],
}
TYPES = ("Infantry", "Cavalry", "Archers")


def per_troop(tier, stats):
    """stats: 3 rows of [atk%, def%, leth%, hp%] for Inf, Cav, Arc."""
    b = BASE[tier]
    att, dfn = [], []
    for i, (atk, de, leth, hp) in enumerate(stats):
        att.append(b[i * 2] * (1 + atk / 100) * 10 * (1 + leth / 100) / 100)
        dfn.append(10 * (1 + de / 100) * b[i * 2 + 1] * (1 + hp / 100) / 100)
    return att, dfn


def _counter(i, t):
    return 1.1 if (i, t) in ((0, 1), (1, 2), (2, 0)) else 1.0


def _hits(n, att, target_n, target_def, army_min, f, rng, out):
    front = next((k for k in range(3) if target_n[k] > 0), None)
    if front is None:
        return
    for i in range(3):
        if n[i] <= 0:
            continue
        base = math.sqrt(n[i] * army_min) * att[i] * f / 100
        mult = 1
        if i == 2:  # archer volley: 10% chance to fire twice
            mult = (2 if rng.random() < 0.1 else 1) if rng else 1.1
        if i == 1 and front != 2 and target_n[2] > 0:
            parts = [((2 if rng.random() < 0.2 else front), 1.0)] if rng else [(front, 0.8), (2, 0.2)]
        else:
            parts = [(front, 1.0)]
        for t, w in parts:
            d = base / target_def[t] * _counter(i, t) * mult * w
            out[t] += math.ceil(d) if rng else d


def battle(n_a, A, n_b, B, rng=None, fatigue=False, max_rounds=5000):
    """Returns (win, rounds, your_left, enemy_left, score).
    win: 1 you win, -1 you lose, 0 draw. rng=None -> expected (deterministic) mode."""
    a, b = list(n_a), list(n_b)
    s_a, s_b = sum(a), sum(b)
    army_min = min(s_a, s_b)
    r = 0
    while r < max_rounds and sum(a) > 0 and sum(b) > 0:
        f = 1 - r * 0.0001 if fatigue else 1
        d_a, d_b = [0.0] * 3, [0.0] * 3
        _hits(a, A[0], b, B[1], army_min, f, rng, d_b)  # you hit enemy
        _hits(b, B[0], a, A[1], army_min, f, rng, d_a)  # enemy hits you
        a = [x - d if x - d >= 1 else 0 for x, d in zip(a, d_a)]
        b = [x - d if x - d >= 1 else 0 for x, d in zip(b, d_b)]
        r += 1
    ta, tb = sum(a), sum(b)
    win = 1 if ta > 0 and tb == 0 else -1 if tb > 0 and ta == 0 else 0
    score = ta / s_a if win > 0 else -tb / s_b if win < 0 else 0
    return win, r, a, b, score


def split(total, inf, cav):
    a, c = round(total * inf / 100), round(total * cav / 100)
    return [a, c, max(0, total - a - c)]


def win_rate(ratio, total, A, n_b, B, runs=300, seed=20260925, fatigue=False):
    """Monte Carlo win rate. Same seed for every ratio = common random numbers."""
    rng = random.Random(seed)
    n_a = split(total, ratio[0], ratio[1])
    wins = score = 0.0
    for _ in range(runs):
        w, _, _, _, s = battle(n_a, A, n_b, B, rng=rng, fatigue=fatigue)
        wins += 1 if w > 0 else 0.5 if w == 0 else 0
        score += s
    return wins / runs, score / runs


def find_best(total, A, n_b, B, runs=300, top=40, fatigue=False):
    sweep = []
    for inf in range(101):
        for cav in range(101 - inf):
            s = battle(split(total, inf, cav), A, n_b, B, fatigue=fatigue)[4]
            sweep.append((s, inf, cav))
    sweep.sort(reverse=True)
    results = []
    for _, inf, cav in sweep[:top]:
        w, s = win_rate((inf, cav), total, A, n_b, B, runs, fatigue=fatigue)
        results.append((w, s, (inf, cav, 100 - inf - cav)))
    results.sort(reverse=True)
    return results


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Find the best Mystic Trial troop ratio.")
    p.add_argument("--runs", type=int, default=300, help="replays per contender")
    args = p.parse_args()

    # Example numbers (replace with the stage's View Details screen): [Atk%, Def%, Leth%, HP%]
    you = [[85, 85, 40, 40], [70, 60, 45, 35], [90, 55, 60, 35]]
    enemy = [[85, 85, 40, 45], [70, 65, 40, 35], [90, 60, 55, 35]]
    A, B = per_troop("T10", you), per_troop("T10", enemy)
    total, enemy_n = 150_000, [75_000, 30_000, 45_000]

    print("Inf/Cav/Arc   win rate   avg margin")
    for w, s, r in find_best(total, A, enemy_n, B, runs=args.runs)[:10]:
        print(f"{r[0]:>3}/{r[1]:>3}/{r[2]:>3}    {w*100:6.1f}%    {s*100:+6.1f}%")
