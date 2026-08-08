"""
D-brane geometry for Theory-5.

D-branes constrain matter movement in Theory-5.  The complex brane structure
built on top of the fermionic string creates the cellular automaton geometry
that defines the Cosmos rules.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Iterator, List, Optional, Sequence, Tuple


@dataclass
class DBrane:
    """
    A D-brane in Theory-5.

    A D-brane is a (d+1)-dimensional object that emerges from the string
    structure.  Its *dimension* attribute specifies *d* (the number of spatial
    dimensions spanned by the brane).

    D-branes constrain the motion of matter and define the boundaries of the
    cellular automaton cells.
    """

    dimension: int          # Spatial dimension of the brane (d in D_d-brane)
    position: Tuple[float, ...] = field(default_factory=tuple)
    tension: float = 1.0   # Brane tension in natural units

    def __post_init__(self) -> None:
        if self.dimension < 0:
            raise ValueError("Brane dimension must be non-negative.")
        if self.tension <= 0:
            raise ValueError("Brane tension must be positive.")
        if self.position and len(self.position) < self.dimension:
            raise ValueError(
                "Position vector length must be at least equal to the brane dimension."
            )

    @property
    def world_volume_dimension(self) -> int:
        """Return the world-volume dimension (d + 1, including time)."""
        return self.dimension + 1

    @property
    def mass(self) -> float:
        """
        Compute the effective mass of the brane.

        In string units: M = T * V_d where V_d is the unit d-volume (set to 1
        here for simplicity; override in sub-classes for non-unit volumes).
        """
        return self.tension  # V_d = 1 in natural units

    def constrains(self, point: Sequence[float]) -> bool:
        """
        Return True if this brane constrains motion at *point*.

        A D_d-brane constrains motion in directions transverse to itself.
        Here we use a simplified criterion: the brane constrains a point if
        the point's coordinate in the first transverse direction equals the
        brane's position in that direction (within numerical tolerance).
        """
        if not self.position or not point:
            return False
        transverse_idx = self.dimension  # first transverse direction
        if transverse_idx >= len(point) or transverse_idx >= len(self.position):
            return False
        return math.isclose(point[transverse_idx], self.position[transverse_idx], rel_tol=1e-9)

    def __repr__(self) -> str:
        return (
            f"DBrane(d={self.dimension}, position={self.position}, "
            f"tension={self.tension})"
        )


@dataclass
class BraneStructure:
    """
    The complex brane structure of Theory-5.

    This structure emerges over the unique fermionic string and creates the
    cellular automaton that supports the holographic geometry.
    """

    branes: List[DBrane] = field(default_factory=list)

    # ------------------------------------------------------------------
    # Building helpers
    # ------------------------------------------------------------------

    @classmethod
    def standard(cls) -> "BraneStructure":
        """
        Create the standard Theory-5 brane configuration.

        The standard configuration contains five D-branes of dimensions 0
        through 4, placed at unit-lattice positions, reflecting the five
        fundamental geometrical roles in Theory-5.
        """
        branes = [
            DBrane(dimension=d, position=tuple(float(i) for i in range(d + 1)))
            for d in range(5)
        ]
        return cls(branes=branes)

    def add_brane(self, brane: DBrane) -> None:
        """Add a brane to the structure."""
        self.branes.append(brane)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def branes_of_dimension(self, d: int) -> List[DBrane]:
        """Return all branes with the given spatial dimension."""
        return [b for b in self.branes if b.dimension == d]

    def constraining_branes(self, point: Sequence[float]) -> List[DBrane]:
        """Return all branes that constrain motion at *point*."""
        return [b for b in self.branes if b.constrains(point)]

    @property
    def total_tension(self) -> float:
        """Return the sum of tensions across all branes."""
        return sum(b.tension for b in self.branes)

    @property
    def dimension_spectrum(self) -> List[int]:
        """Return sorted list of distinct brane dimensions present."""
        return sorted({b.dimension for b in self.branes})

    @property
    def cell_count(self) -> int:
        """
        Approximate number of automaton cells.

        In Theory-5 each pair of adjacent D-branes forms a cell boundary.
        The number of cells equals the number of adjacent brane pairs.
        """
        dims = self.dimension_spectrum
        if len(dims) < 2:
            return 1
        return len(dims) - 1

    def iter_cells(self) -> Iterator[Tuple[DBrane, DBrane]]:
        """Iterate over adjacent brane pairs (cellular automaton cells)."""
        dims = self.dimension_spectrum
        brane_map = {d: self.branes_of_dimension(d)[0] for d in dims if self.branes_of_dimension(d)}
        for i in range(len(dims) - 1):
            yield brane_map[dims[i]], brane_map[dims[i + 1]]

    def __repr__(self) -> str:
        return f"BraneStructure(branes={len(self.branes)}, dimensions={self.dimension_spectrum})"
