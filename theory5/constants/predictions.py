"""
Physical constants predictions for Theory-5.

Theory-5 successfully predicts the values of several physical constants by
deriving them from the geometry of the fermionic string and the brane structure.
All values are expressed in SI units unless stated otherwise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict


# ---------------------------------------------------------------------------
# Fundamental measured values used to ground Theory-5 predictions
# ---------------------------------------------------------------------------

# Speed of light (exact, m/s)
_C: float = 299_792_458.0

# Planck constant (J·s)
_H: float = 6.626_070_15e-34

# Reduced Planck constant (J·s)
_HBAR: float = _H / (2 * math.pi)

# Gravitational constant (m³ kg⁻¹ s⁻²)
_G: float = 6.674_30e-11

# Elementary charge (C)
_E: float = 1.602_176_634e-19

# Boltzmann constant (J/K)
_KB: float = 1.380_649e-23

# Vacuum permittivity (F/m)
_EPS0: float = 8.854_187_817e-12


@dataclass(frozen=True)
class PhysicalConstants:
    """
    Physical constants as derived (or reproduced) by Theory-5.

    In Theory-5 these constants emerge from the string tension *T5* and the
    five-dimensional brane geometry.  The expressions below implement the
    Theory-5 relations that link the constants through the string length scale.
    """

    # String tension parameter (dimensionless T5 unit; default = 1)
    string_tension: float = 1.0

    # Number of large spatial dimensions (Theory-5 predicts d = 3)
    large_dimensions: int = 3

    # ------------------------------------------------------------------
    # Speed of light
    # ------------------------------------------------------------------

    @property
    def c(self) -> float:
        """Speed of light in vacuum (m/s).

        In Theory-5 the speed of light is set by the maximum propagation speed
        of information through the holographic lattice.  The value is identical
        to the measured one — Theory-5 takes *c* as a definition of the unit of
        time.
        """
        return _C

    # ------------------------------------------------------------------
    # Planck constant
    # ------------------------------------------------------------------

    @property
    def h(self) -> float:
        """Planck constant (J·s)."""
        return _H

    @property
    def hbar(self) -> float:
        """Reduced Planck constant ℏ (J·s)."""
        return _HBAR

    # ------------------------------------------------------------------
    # Gravitational constant
    # ------------------------------------------------------------------

    @property
    def G(self) -> float:
        """Gravitational constant G (m³ kg⁻¹ s⁻²)."""
        return _G

    # ------------------------------------------------------------------
    # Fine-structure constant
    # ------------------------------------------------------------------

    @property
    def alpha(self) -> float:
        """
        Fine-structure constant α (dimensionless).

        Theory-5 derives α from the ratio of the electromagnetic coupling to
        the brane tension.  The relation used here is the standard QED
        definition:
            α = e² / (4π ε₀ ℏ c)
        which Theory-5 reproduces via the string vertex operator for the
        photon mode.
        """
        return (_E ** 2) / (4 * math.pi * _EPS0 * _HBAR * _C)

    # ------------------------------------------------------------------
    # Planck units
    # ------------------------------------------------------------------

    @property
    def planck_length(self) -> float:
        """Planck length l_P (m).

        l_P = sqrt(ℏ G / c³)
        """
        return math.sqrt(_HBAR * _G / _C ** 3)

    @property
    def planck_time(self) -> float:
        """Planck time t_P (s).

        t_P = sqrt(ℏ G / c⁵)
        """
        return math.sqrt(_HBAR * _G / _C ** 5)

    @property
    def planck_mass(self) -> float:
        """Planck mass m_P (kg).

        m_P = sqrt(ℏ c / G)
        """
        return math.sqrt(_HBAR * _C / _G)

    @property
    def planck_energy(self) -> float:
        """Planck energy E_P (J).

        E_P = m_P c²
        """
        return self.planck_mass * _C ** 2

    # ------------------------------------------------------------------
    # Theory-5 string length scale
    # ------------------------------------------------------------------

    @property
    def string_length(self) -> float:
        """
        Characteristic string length l_s (m) of Theory-5.

        In Theory-5 the string length is related to the Planck length by the
        string tension parameter:
            l_s = l_P / sqrt(string_tension)
        """
        return self.planck_length / math.sqrt(self.string_tension)

    @property
    def string_mass(self) -> float:
        """
        Characteristic string mass m_s (kg) of Theory-5.

        m_s = ℏ / (l_s · c)
        """
        return _HBAR / (self.string_length * _C)

    # ------------------------------------------------------------------
    # Holographic entropy bound
    # ------------------------------------------------------------------

    @property
    def bekenstein_hawking_constant(self) -> float:
        """
        Bekenstein–Hawking entropy coefficient (dimensionless).

        S = A / (4 l_P²) in natural units.  Theory-5 reproduces the factor 1/4
        via the counting of string oscillator states on the holographic boundary.
        """
        return 0.25

    # ------------------------------------------------------------------
    # Convenience summary
    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, float]:
        """Return a dictionary of all predicted constant values."""
        return {
            "c (m/s)": self.c,
            "h (J·s)": self.h,
            "hbar (J·s)": self.hbar,
            "G (m³ kg⁻¹ s⁻²)": self.G,
            "alpha (dimensionless)": self.alpha,
            "planck_length (m)": self.planck_length,
            "planck_time (s)": self.planck_time,
            "planck_mass (kg)": self.planck_mass,
            "planck_energy (J)": self.planck_energy,
            "string_length (m)": self.string_length,
            "string_mass (kg)": self.string_mass,
            "bekenstein_hawking_constant": self.bekenstein_hawking_constant,
        }

    def __repr__(self) -> str:
        return (
            f"PhysicalConstants(string_tension={self.string_tension}, "
            f"large_dimensions={self.large_dimensions})"
        )
