"""
Cellular automaton module for Theory-5.

The cellular automaton arises from the complex brane structure that sits on top
of the unique fermionic string.  It constrains matter movement via D-branes and
underpins the holographic reality we perceive.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterator, List, Optional, Sequence, Tuple

from theory5.geometry.brane import BraneStructure, DBrane


# A Cell is identified by its integer coordinates in the automaton lattice.
CellCoord = Tuple[int, ...]

# A state value stored at each cell.
CellState = int


@dataclass
class Cell:
    """A single cell in the Theory-5 cellular automaton."""

    coord: CellCoord
    state: CellState = 0
    brane: Optional[DBrane] = None  # constraining D-brane (if any)

    def __hash__(self) -> int:
        return hash(self.coord)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Cell):
            return self.coord == other.coord
        return NotImplemented

    def __repr__(self) -> str:
        return f"Cell(coord={self.coord}, state={self.state})"


# Default transition rule: majority vote among neighbours (binary states 0/1)
def _majority_rule(cell: Cell, neighbours: List[Cell]) -> CellState:
    if not neighbours:
        return cell.state
    total = sum(n.state for n in neighbours)
    threshold = len(neighbours) / 2
    return 1 if total > threshold else 0


@dataclass
class CellularAutomaton:
    """
    The holographic cellular automaton of Theory-5.

    The automaton is defined over a lattice whose cells are bounded by D-branes.
    Each cell evolves according to a local transition rule that captures the
    computational logic of the holographic reality.
    """

    brane_structure: BraneStructure
    dimensions: int = 3
    size: int = 8  # Number of cells per spatial dimension

    # Internal state: coord → Cell
    _cells: Dict[CellCoord, Cell] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.dimensions not in (1, 2, 3):
            raise ValueError(
                f"Unsupported number of dimensions: {self.dimensions}. "
                "CellularAutomaton supports 1, 2, or 3 spatial dimensions."
            )
        # Store rule as a plain instance attribute to avoid descriptor binding.
        object.__setattr__(self, "_rule", _majority_rule)
        self._initialise_lattice()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def _initialise_lattice(self) -> None:
        """Populate the lattice with cells in the ground state."""
        self._cells = {}
        for coord in self._all_coords():
            self._cells[coord] = Cell(coord=coord, state=0)

    def _all_coords(self) -> Iterator[CellCoord]:
        """Yield every lattice coordinate."""
        if self.dimensions == 1:
            for x in range(self.size):
                yield (x,)
        elif self.dimensions == 2:
            for x in range(self.size):
                for y in range(self.size):
                    yield (x, y)
        else:
            for x in range(self.size):
                for y in range(self.size):
                    for z in range(self.size):
                        yield (x, y, z)

    # ------------------------------------------------------------------
    # State access
    # ------------------------------------------------------------------

    def get_state(self, coord: CellCoord) -> CellState:
        """Return the current state of the cell at *coord*."""
        return self._cells[coord].state

    def set_state(self, coord: CellCoord, state: CellState) -> None:
        """Set the state of the cell at *coord*."""
        self._cells[coord].state = state

    def set_rule(self, rule: Callable[[Cell, List[Cell]], CellState]) -> None:
        """Replace the transition rule."""
        object.__setattr__(self, "_rule", rule)

    # ------------------------------------------------------------------
    # Neighbours
    # ------------------------------------------------------------------

    def neighbours(self, coord: CellCoord) -> List[Cell]:
        """Return the von Neumann neighbourhood cells of *coord*."""
        result: List[Cell] = []
        for axis in range(len(coord)):
            for delta in (-1, +1):
                nc = list(coord)
                nc[axis] += delta
                # Periodic boundary conditions
                nc[axis] = nc[axis] % self.size
                nb_coord = tuple(nc)
                if nb_coord in self._cells:
                    result.append(self._cells[nb_coord])
        return result

    # ------------------------------------------------------------------
    # Evolution
    # ------------------------------------------------------------------

    def step(self) -> None:
        """Advance the automaton by one generation."""
        new_states: Dict[CellCoord, CellState] = {}
        for coord, cell in self._cells.items():
            nbs = self.neighbours(coord)
            new_states[coord] = self._rule(cell, nbs)
        for coord, state in new_states.items():
            self._cells[coord].state = state

    def run(self, steps: int) -> None:
        """Run the automaton for *steps* generations."""
        for _ in range(steps):
            self.step()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    @property
    def active_cells(self) -> int:
        """Return the number of cells currently in the active (1) state."""
        return sum(1 for c in self._cells.values() if c.state == 1)

    @property
    def total_cells(self) -> int:
        """Return the total number of cells in the lattice."""
        return len(self._cells)

    @property
    def density(self) -> float:
        """Return the fraction of active cells."""
        if self.total_cells == 0:
            return 0.0
        return self.active_cells / self.total_cells

    def snapshot(self) -> Dict[CellCoord, CellState]:
        """Return a copy of the current lattice state."""
        return {coord: cell.state for coord, cell in self._cells.items()}

    def __repr__(self) -> str:
        return (
            f"CellularAutomaton(dimensions={self.dimensions}, size={self.size}, "
            f"total_cells={self.total_cells}, active={self.active_cells})"
        )
