"""Tests for the Theory-5 cellular automaton."""

import pytest

from theory5.automaton.cellular import CellularAutomaton, Cell, _majority_rule
from theory5.geometry.brane import BraneStructure


@pytest.fixture
def standard_automaton():
    bs = BraneStructure.standard()
    return CellularAutomaton(brane_structure=bs, dimensions=1, size=8)


class TestCell:
    def test_hash_by_coord(self):
        c1 = Cell(coord=(0, 0))
        c2 = Cell(coord=(0, 0))
        assert c1 == c2
        assert hash(c1) == hash(c2)

    def test_distinct_coords(self):
        c1 = Cell(coord=(0, 0))
        c2 = Cell(coord=(0, 1))
        assert c1 != c2


class TestMajorityRule:
    def test_majority_active(self):
        cell = Cell(coord=(0,), state=0)
        neighbours = [Cell(coord=(i,), state=1) for i in range(3)]
        assert _majority_rule(cell, neighbours) == 1

    def test_majority_inactive(self):
        cell = Cell(coord=(0,), state=1)
        neighbours = [Cell(coord=(i,), state=0) for i in range(3)]
        assert _majority_rule(cell, neighbours) == 0

    def test_no_neighbours_unchanged(self):
        cell = Cell(coord=(0,), state=1)
        assert _majority_rule(cell, []) == 1


class TestCellularAutomaton:
    def test_total_cells_1d(self, standard_automaton):
        ca = standard_automaton
        assert ca.total_cells == 8

    def test_initial_density_zero(self, standard_automaton):
        ca = standard_automaton
        assert ca.density == 0.0

    def test_set_and_get_state(self, standard_automaton):
        ca = standard_automaton
        ca.set_state((3,), 1)
        assert ca.get_state((3,)) == 1

    def test_active_cells_count(self, standard_automaton):
        ca = standard_automaton
        ca.set_state((0,), 1)
        ca.set_state((4,), 1)
        assert ca.active_cells == 2

    def test_step_does_not_raise(self, standard_automaton):
        ca = standard_automaton
        ca.set_state((0,), 1)
        ca.step()  # should not raise

    def test_run_multiple_steps(self, standard_automaton):
        ca = standard_automaton
        ca.run(10)
        assert ca.total_cells == 8

    def test_snapshot_copy(self, standard_automaton):
        ca = standard_automaton
        ca.set_state((1,), 1)
        snap = ca.snapshot()
        ca.set_state((1,), 0)
        # snapshot should not change
        assert snap[(1,)] == 1

    def test_neighbours_periodic(self, standard_automaton):
        ca = standard_automaton
        nbs = ca.neighbours((0,))
        coords = [n.coord for n in nbs]
        # Periodic: neighbour at index -1 wraps to 7
        assert (7,) in coords
        assert (1,) in coords

    def test_custom_rule(self, standard_automaton):
        ca = standard_automaton
        ca.set_rule(lambda cell, nbs: 1)
        ca.step()
        assert ca.active_cells == ca.total_cells

    def test_invalid_dimensions_raises(self):
        bs = BraneStructure.standard()
        with pytest.raises(ValueError):
            CellularAutomaton(brane_structure=bs, dimensions=4, size=4)

    def test_2d_automaton(self):
        bs = BraneStructure.standard()
        ca = CellularAutomaton(brane_structure=bs, dimensions=2, size=4)
        assert ca.total_cells == 16

    def test_3d_automaton(self):
        bs = BraneStructure.standard()
        ca = CellularAutomaton(brane_structure=bs, dimensions=3, size=4)
        assert ca.total_cells == 64
