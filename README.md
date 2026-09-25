# Mystic Trial Ratio Lab

A calculator for **Kingshot's Mystic Trial** that finds the infantry / cavalry / archer ratio that wins most often, based on your stats and the enemy's.

**▶ Use it online:** https://negev16.github.io/mystic-trial-ratio-lab/  
**Source code:** https://github.com/negev16/mystic-trial-ratio-lab

The usual community ratios (50/20/30, 60/15/25…) are only starting points. From Monday to Saturday both sides fight with identical level-10 troops, so the result depends on which line collapses first and in which round. A 1% change can turn a loss into a win.

## How it works

1. **Full sweep:** it simulates the fight for every split at 1% steps (5,151 combinations) with the expected-value battle model.
2. **Replays:** it reruns the top 40, plus the community start ratio and your current ratio, 100–1,000 times with the random procs included. Every ratio gets the same random rolls (common random numbers), so the ranking compares ratios, not luck.
3. **Upgrade check:** it adds +5 points to each stat, one at a time, to show which upgrade in that zone helps most.

### Battle model

```
attack  = base_atk × (1+Atk%) × 10 × (1+Leth%) / 100
defense = 10 × (1+Def%) × base_hp × (1+HP%) / 100
army    = √(squad troops × smaller army total)
kills   = army × attack / enemy defense × counter / 100
```

- Each squad hits the first enemy line still standing: infantry → cavalry → archers.
- Counter hits (Inf→Cav, Cav→Arc, Arc→Inf) deal +10%.
- Cavalry skip to the archers 20% of rounds. Archers fire twice 10% of rounds.
- Both sides hit at the same time. The fight runs until one side has no troops left.
- Optional: round fatigue (−0.01% damage per round).

## Using it

1. Pick the zone: Forest of Life, Crystal Cave, Knowledge Nexus, Molten Fort (Coliseum and Radiant Spire are supported, but hero skills aren't simulated).
2. Before fighting, tap the stage's **View Details**. It shows *My Stats* and *Opponent's Stats* plus the enemy troop counts, and checking it doesn't use an attempt.
3. Copy the Attack / Defense / Lethality / Health % for all three troop types, **yours and the enemy's**, plus the enemy troop counts.
4. Press **Find best ratio**. Use 1,000 replays when the result matters: win rates from 100 replays are only accurate to about ±5%.

Your numbers are saved in your browser, per zone.

## Files

| File | What it is |
|---|---|
| `index.html` | The calculator. One self-contained file, HTML + JavaScript, no install. |
| `battle_sim.py` | The same engine in Python (standard library only) for testing and analysis. Run `python battle_sim.py --runs 1000`. |

## Limits

- The formula is the community's reverse-engineering of the combat engine shared with State of Survival, checked against Kingshot battle reports. It is **not official**.
- Hero skills and pet skills are not simulated, so Coliseum, Radiant Spire and Forest of Life are less precise.
- The results are only as good as the stats you enter.

## Ideas for contributions

- Hero skill effects (SkillMod) for Coliseum / Radiant Spire
- Pet skills for Forest of Life
- Confidence intervals next to each win rate
- Verified base stats for more troop tiers

## Credits

The battle formula and troop base stats come from community research:
- [Absy Labs – Kingshot damage formula](https://kingshotsim.com/damage-formula.html) and [troop base stats](https://kingshotsim.com/rally-and-troops.html)
- [Kingshot Guides – Bear Trap damage mechanics](https://kingshotguides.com/guide/bear-trap-damage-mechanics-and-example-simulation/)
- [Kingshot Almanach – Mystic Trial zones and start ratios](https://kingshotalmanach.com/events/mystic-trial/)

## License

MIT © 2026 negev16. See [LICENSE](LICENSE).

*Fan-made tool. Not affiliated with or endorsed by Kingshot or Century Games.*
