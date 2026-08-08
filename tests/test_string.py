"""Tests for the FermionicString model."""

import math
import pytest

from theory5.models.string import (
    FermionicString,
    VibrationalState,
    MODE_CONFIGURATIONS,
    VIBRATIONAL_MODES,
)


class TestVibrationalState:
    def test_ground_state_energy(self):
        state = VibrationalState(mode=0, amplitude=1.0)
        assert math.isclose(state.energy, 0.5)

    def test_first_mode_energy(self):
        state = VibrationalState(mode=1, amplitude=1.0)
        assert math.isclose(state.energy, 1.5)

    def test_configuration_label(self):
        assert VibrationalState(mode=0).configuration == "scalar"
        assert VibrationalState(mode=1).configuration == "spinor"
        assert VibrationalState(mode=5).configuration == "graviton"

    def test_unknown_mode_label(self):
        state = VibrationalState(mode=99)
        assert state.configuration == "mode_99"

    def test_wavefunction_phase(self):
        state = VibrationalState(mode=0, amplitude=1.0, phase=math.pi / 2)
        wf = state.wavefunction
        assert math.isclose(wf.real, 0.0, abs_tol=1e-10)
        assert math.isclose(wf.imag, 1.0)

    def test_superpose(self):
        s1 = VibrationalState(mode=0, amplitude=1.0, phase=0.0)
        s2 = VibrationalState(mode=1, amplitude=1.0, phase=0.0)
        sup = s1.superpose(s2)
        assert sup.mode == 1
        assert math.isclose(sup.amplitude, 2.0)

    def test_negative_mode_raises(self):
        with pytest.raises(ValueError):
            VibrationalState(mode=-1)


class TestFermionicString:
    def test_ground_state_factory(self):
        fs = FermionicString.ground_state()
        assert len(fs.states) == 1
        assert fs.states[0].mode == 0

    def test_from_mode_factory(self):
        fs = FermionicString.from_mode(mode=3, amplitude=2.0)
        assert fs.states[0].mode == 3
        assert fs.states[0].amplitude == 2.0

    def test_total_energy(self):
        fs = FermionicString.ground_state(tension=2.0)
        # energy = tension * (mode + 0.5) * amplitude = 2.0 * 0.5 * 1.0
        assert math.isclose(fs.total_energy, 1.0)

    def test_excite_adds_state(self):
        fs = FermionicString.ground_state()
        fs.excite(mode=2)
        assert len(fs.states) == 2

    def test_dominant_state(self):
        fs = FermionicString.ground_state()
        fs.excite(mode=4)
        assert fs.dominant_state is not None
        assert fs.dominant_state.mode == 4

    def test_configurations(self):
        fs = FermionicString.ground_state()
        fs.excite(mode=5)
        cfgs = fs.configurations
        assert "scalar" in cfgs
        assert "graviton" in cfgs

    def test_spectrum_keys(self):
        fs = FermionicString.ground_state()
        spec = fs.spectrum()
        assert "scalar" in spec

    def test_winding_number(self):
        fs = FermionicString.ground_state()
        assert fs.winding_number() == 1
        fs.excite(mode=1)
        assert fs.winding_number() == 2

    def test_collapse_to_dominant(self):
        fs = FermionicString.ground_state()
        fs.excite(mode=3)
        fs.collapse_to_dominant()
        assert len(fs.states) == 1
        assert fs.states[0].mode == 3

    def test_invalid_tension(self):
        with pytest.raises(ValueError):
            FermionicString(tension=-1.0)

    def test_invalid_length(self):
        with pytest.raises(ValueError):
            FermionicString(length=0.0)
