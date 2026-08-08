"""Tests for D-brane geometry."""

import math
import pytest

from theory5.geometry.brane import DBrane, BraneStructure


class TestDBrane:
    def test_world_volume_dimension(self):
        b = DBrane(dimension=2)
        assert b.world_volume_dimension == 3

    def test_mass(self):
        b = DBrane(dimension=1, tension=3.0)
        assert math.isclose(b.mass, 3.0)

    def test_constrains_true(self):
        b = DBrane(dimension=1, position=(0.0, 5.0))
        # transverse direction is index 1; point[1] == 5.0 → constrained
        assert b.constrains((3.0, 5.0))

    def test_constrains_false(self):
        b = DBrane(dimension=1, position=(0.0, 5.0))
        assert not b.constrains((3.0, 7.0))

    def test_negative_dimension_raises(self):
        with pytest.raises(ValueError):
            DBrane(dimension=-1)

    def test_negative_tension_raises(self):
        with pytest.raises(ValueError):
            DBrane(dimension=0, tension=-0.5)

    def test_position_too_short_raises(self):
        with pytest.raises(ValueError):
            DBrane(dimension=3, position=(1.0,))


class TestBraneStructure:
    def test_standard_has_five_branes(self):
        bs = BraneStructure.standard()
        assert len(bs.branes) == 5

    def test_standard_dimension_spectrum(self):
        bs = BraneStructure.standard()
        assert bs.dimension_spectrum == [0, 1, 2, 3, 4]

    def test_total_tension(self):
        bs = BraneStructure()
        bs.add_brane(DBrane(dimension=0, tension=1.0))
        bs.add_brane(DBrane(dimension=1, tension=2.0))
        assert math.isclose(bs.total_tension, 3.0)

    def test_branes_of_dimension(self):
        bs = BraneStructure.standard()
        d2_branes = bs.branes_of_dimension(2)
        assert len(d2_branes) == 1
        assert d2_branes[0].dimension == 2

    def test_cell_count(self):
        bs = BraneStructure.standard()
        # 5 distinct dimensions → 4 adjacent pairs
        assert bs.cell_count == 4

    def test_iter_cells(self):
        bs = BraneStructure.standard()
        cells = list(bs.iter_cells())
        assert len(cells) == 4
        for low, high in cells:
            assert high.dimension == low.dimension + 1

    def test_constraining_branes(self):
        bs = BraneStructure()
        b = DBrane(dimension=0, position=(3.0,))
        bs.add_brane(b)
        result = bs.constraining_branes((3.0,))
        assert b in result
