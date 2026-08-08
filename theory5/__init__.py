"""
Theory-5: A fermionic string-based framework for physical reality.

Theory-5 explains physical reality using a fermionic string structure over which
a geometry emerges that supports computations, allowing the generation of the
holographic reality we perceive.  The structure is composed of a unique string
with a complex brane structure that creates a cellular automaton.
"""

from theory5.models.string import FermionicString
from theory5.geometry.brane import DBrane, BraneStructure
from theory5.automaton.cellular import CellularAutomaton
from theory5.constants.predictions import PhysicalConstants

__all__ = [
    "FermionicString",
    "DBrane",
    "BraneStructure",
    "CellularAutomaton",
    "PhysicalConstants",
]

__version__ = "0.1.0"
