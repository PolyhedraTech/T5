"""
Fermionic string model for Theory-5.

In Theory-5 the fundamental entity is a single fermionic string.  Its different
vibrational modes give rise to the elementary building blocks (analogous to
particles) that compose the computational structure underlying the holographic
reality we perceive.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# Vibrational modes recognised by Theory-5
VIBRATIONAL_MODES: Dict[str, int] = {
    "ground": 0,
    "first": 1,
    "second": 2,
    "third": 3,
    "fourth": 4,
    "fifth": 5,
}

# Each mode maps to a symbolic configuration label used when building the
# brane structure.
MODE_CONFIGURATIONS: Dict[int, str] = {
    0: "scalar",
    1: "spinor",
    2: "vector",
    3: "tensor",
    4: "gravitino",
    5: "graviton",
}


@dataclass
class VibrationalState:
    """Represents the vibrational state of a fermionic string segment."""

    mode: int
    amplitude: float = 1.0
    phase: float = 0.0

    def __post_init__(self) -> None:
        if self.mode < 0:
            raise ValueError("Vibrational mode must be a non-negative integer.")

    @property
    def configuration(self) -> str:
        """Return the configuration label associated with this mode."""
        return MODE_CONFIGURATIONS.get(self.mode, f"mode_{self.mode}")

    @property
    def energy(self) -> float:
        """Return the characteristic energy of the vibrational state.

        Energy scales as (mode + 1/2) * amplitude in natural units of Theory-5.
        """
        return (self.mode + 0.5) * self.amplitude

    @property
    def wavefunction(self) -> complex:
        """Return the complex wavefunction amplitude for this state."""
        return self.amplitude * complex(
            math.cos(self.phase), math.sin(self.phase)
        )

    def superpose(self, other: "VibrationalState") -> "VibrationalState":
        """Return the superposition of two vibrational states."""
        combined = self.wavefunction + other.wavefunction
        new_amplitude = abs(combined)
        new_phase = math.atan2(combined.imag, combined.real)
        new_mode = max(self.mode, other.mode)
        return VibrationalState(mode=new_mode, amplitude=new_amplitude, phase=new_phase)


@dataclass
class FermionicString:
    """
    The fundamental entity of Theory-5.

    A single fermionic string whose vibrational modes give rise to all of the
    configurations needed to build the computational geometry and cellular
    automaton that underpin holographic reality.
    """

    states: List[VibrationalState] = field(default_factory=list)
    tension: float = 1.0  # String tension in natural units (T5)
    length: float = 1.0   # Proper length of the string segment

    def __post_init__(self) -> None:
        if self.tension <= 0:
            raise ValueError("String tension must be positive.")
        if self.length <= 0:
            raise ValueError("String length must be positive.")

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    @classmethod
    def ground_state(cls, tension: float = 1.0, length: float = 1.0) -> "FermionicString":
        """Create a string in the ground vibrational state."""
        return cls(
            states=[VibrationalState(mode=0)],
            tension=tension,
            length=length,
        )

    @classmethod
    def from_mode(
        cls,
        mode: int,
        amplitude: float = 1.0,
        phase: float = 0.0,
        tension: float = 1.0,
        length: float = 1.0,
    ) -> "FermionicString":
        """Create a string in a specific vibrational mode."""
        return cls(
            states=[VibrationalState(mode=mode, amplitude=amplitude, phase=phase)],
            tension=tension,
            length=length,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def total_energy(self) -> float:
        """Sum of energies across all vibrational states, weighted by tension."""
        return self.tension * sum(s.energy for s in self.states)

    @property
    def dominant_state(self) -> Optional[VibrationalState]:
        """Return the vibrational state with the highest energy."""
        if not self.states:
            return None
        return max(self.states, key=lambda s: s.energy)

    @property
    def configurations(self) -> List[str]:
        """Return all configuration labels present in this string."""
        return [s.configuration for s in self.states]

    # ------------------------------------------------------------------
    # Operations
    # ------------------------------------------------------------------

    def excite(self, mode: int, amplitude: float = 1.0, phase: float = 0.0) -> None:
        """Add a new vibrational excitation to the string."""
        self.states.append(VibrationalState(mode=mode, amplitude=amplitude, phase=phase))

    def collapse_to_dominant(self) -> None:
        """Collapse all states to the single dominant vibrational state."""
        dom = self.dominant_state
        if dom is not None:
            self.states = [dom]

    def spectrum(self) -> Dict[str, float]:
        """Return a mapping of configuration label → energy contribution."""
        result: Dict[str, float] = {}
        for state in self.states:
            label = state.configuration
            result[label] = result.get(label, 0.0) + self.tension * state.energy
        return result

    def mode_numbers(self) -> List[int]:
        """Return a sorted list of all active mode numbers."""
        return sorted({s.mode for s in self.states})

    def winding_number(self) -> int:
        """
        Compute the winding number of the string around the compact dimension.

        In Theory-5, the winding number is the count of distinct mode levels.
        """
        return len(set(s.mode for s in self.states))

    def __repr__(self) -> str:
        modes = [s.mode for s in self.states]
        return (
            f"FermionicString(tension={self.tension}, length={self.length}, "
            f"modes={modes}, total_energy={self.total_energy:.4f})"
        )
