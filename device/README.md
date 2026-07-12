# /device: the physical embodiments

Three documents live here, one per altitude:

| document | what it is |
|---|---|
| [TRANSISTOR.md](TRANSISTOR.md) | **the unit**: one pinout (GATE, SOURCE, DRAIN, CHANNEL, BODY) at three scales (benchtop, crystal, reactor), the valve, the load bearing analogy table, the gain bandwidth theorem, and the datasheet with characteristic curves (figure 12) and absolute maximum ratings |
| [SEALED.md](SEALED.md) | **the machine**: the ampoule, a sealed self sustaining unit with no penetrations; architecture, the lamp arithmetic and its repair, the inventory ledger, aging curves, and the boundary, all computed by [`sealed_unit.py`](sealed_unit.py) into [`sealed_results.md`](sealed_results.md) and figure 11 |
| [SCALING.md](SCALING.md) | **the trajectory**: the ENIAC ledger of component levers, physical ceilings, and the borrowed industrial curves that improve each part for free |

Scripts: [`make_transistor_figure.py`](make_transistor_figure.py) (figure 10), [`make_datasheet_figure.py`](make_datasheet_figure.py) (figure 12), [`sealed_unit.py`](sealed_unit.py) (figure 11 and every number in SEALED.md). All deterministic; all run in CI.
