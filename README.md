# T5 — Theory-5

> *"We present Theory-5, an approach to explain our physical reality using a
> fermionic string structure. Over this structure, a geometry emerges, that
> supports computations, allowing the generation of the holographic reality we
> perceive."*

## Overview

Theory-5 (T5) is a theoretical-physics framework that explains physical reality
through a unique fermionic string.  The string exhibits different vibrational
modes that give rise to the elementary building blocks of the computational
structure underlying the holographic reality we experience.

Key concepts:

| Concept | Description |
|---|---|
| **Fermionic string** | The single fundamental entity; its vibrational modes produce all field configurations (scalar, spinor, vector, tensor, gravitino, graviton). |
| **D-branes** | Higher-dimensional objects that bound and constrain matter movement within the computational geometry. |
| **Brane structure** | The complex arrangement of D-branes over the string that generates the cellular automaton. |
| **Cellular automaton** | The discrete computational substrate that produces the holographic reality. |
| **Physical constants** | T5 predicts α, G, Planck units, and string-scale quantities from first principles. |

## Package structure

```
theory5/
├── models/
│   └── string.py          # FermionicString and VibrationalState
├── geometry/
│   └── brane.py           # DBrane and BraneStructure
├── automaton/
│   └── cellular.py        # CellularAutomaton
└── constants/
    └── predictions.py     # PhysicalConstants
```

## Quick start

```python
from theory5 import FermionicString, BraneStructure, CellularAutomaton, PhysicalConstants

# Create a fermionic string in the ground state and excite two modes
fs = FermionicString.ground_state(tension=1.0)
fs.excite(mode=1)   # spinor mode
fs.excite(mode=5)   # graviton mode
print(fs)
# FermionicString(tension=1.0, length=1.0, modes=[0, 1, 5], total_energy=3.5000)

# Build the standard brane structure (D0 … D4)
bs = BraneStructure.standard()

# Initialise the 3-D cellular automaton (8³ = 512 cells)
ca = CellularAutomaton(brane_structure=bs, dimensions=3, size=8)
ca.set_state((0, 0, 0), 1)
ca.run(steps=10)
print(f"Active cells after 10 steps: {ca.active_cells} / {ca.total_cells}")

# Inspect predicted physical constants
pc = PhysicalConstants()
print(f"Fine-structure constant α ≈ {pc.alpha:.6f}")   # ≈ 1/137
print(f"Planck length  l_P = {pc.planck_length:.4e} m")
print(f"String length  l_s = {pc.string_length:.4e} m")
```

## Running the tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Theory summary

Theory-5 places a unique fermionic string at the foundation of reality.
The string's vibrational spectrum generates five field configurations that map
to the five geometrical roles in the theory (scalar through graviton).  A
complex D-brane structure built over the string defines the topology of a
cellular automaton whose evolution reproduces the large-scale holographic
geometry we observe as the Cosmos.

The framework provides a common basis for both quantum mechanics and general
relativity by deriving the fine-structure constant, Planck units, and the
Bekenstein–Hawking entropy coefficient from a single string tension parameter.

## License

MIT — see [LICENSE](LICENSE).
