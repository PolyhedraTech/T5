"""Tests for Theory-5 physical constants predictions."""

import math
import pytest

from theory5.constants.predictions import PhysicalConstants


@pytest.fixture
def pc():
    return PhysicalConstants()


class TestPhysicalConstants:
    def test_speed_of_light(self, pc):
        assert math.isclose(pc.c, 299_792_458.0)

    def test_planck_constant(self, pc):
        assert math.isclose(pc.h, 6.626_070_15e-34, rel_tol=1e-9)

    def test_hbar_relation(self, pc):
        assert math.isclose(pc.hbar, pc.h / (2 * math.pi))

    def test_gravitational_constant(self, pc):
        assert math.isclose(pc.G, 6.674_30e-11, rel_tol=1e-9)

    def test_fine_structure_constant_approx(self, pc):
        # α ≈ 1/137 ≈ 0.00729735
        assert math.isclose(pc.alpha, 1 / 137.036, rel_tol=1e-4)

    def test_planck_length_positive(self, pc):
        assert pc.planck_length > 0

    def test_planck_time_positive(self, pc):
        assert pc.planck_time > 0

    def test_planck_mass_positive(self, pc):
        assert pc.planck_mass > 0

    def test_planck_energy_positive(self, pc):
        assert pc.planck_energy > 0

    def test_planck_energy_equals_mass_c2(self, pc):
        assert math.isclose(pc.planck_energy, pc.planck_mass * pc.c ** 2)

    def test_string_length_default_tension(self, pc):
        # With tension=1, string_length == planck_length
        assert math.isclose(pc.string_length, pc.planck_length)

    def test_string_length_higher_tension(self):
        pc2 = PhysicalConstants(string_tension=4.0)
        assert math.isclose(pc2.string_length, pc2.planck_length / 2.0)

    def test_string_mass_positive(self, pc):
        assert pc.string_mass > 0

    def test_bekenstein_hawking_constant(self, pc):
        assert math.isclose(pc.bekenstein_hawking_constant, 0.25)

    def test_summary_has_expected_keys(self, pc):
        s = pc.summary()
        assert "c (m/s)" in s
        assert "alpha (dimensionless)" in s
        assert "planck_length (m)" in s
        assert "string_length (m)" in s
