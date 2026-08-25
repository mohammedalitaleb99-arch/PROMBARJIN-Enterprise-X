import numpy as np
import pytest

from app.quantum import QuantumState


def test_h_gate_and_sampling_are_non_collapsing():
    q = QuantumState(1).h(0)
    before = q.statevector()
    probs = q.probabilities()
    assert np.allclose(probs, [0.5, 0.5])
    _ = q.sample(5000, seed=123)
    assert np.allclose(q.statevector(), before)


def test_x_and_double_h():
    assert np.allclose(QuantumState(1).x(0).statevector(), [0, 1])
    assert np.allclose(QuantumState(1).h(0).h(0).statevector(), [1, 0])


def test_bell_state_distribution():
    q = QuantumState.bell_state()
    probs = q.probabilities()
    assert np.isclose(probs[0], 0.5, atol=1e-12)
    assert np.isclose(probs[3], 0.5, atol=1e-12)
    assert np.isclose(probs[1], 0.0, atol=1e-12)
    assert np.isclose(probs[2], 0.0, atol=1e-12)
    assert q.is_normalized()


def test_ghz_state_distribution():
    q = QuantumState.ghz_state(3)
    probs = q.probabilities()
    assert np.isclose(probs[0], 0.5, atol=1e-12)
    assert np.isclose(probs[7], 0.5, atol=1e-12)
    assert np.isclose(probs[1:7].sum(), 0.0, atol=1e-12)


def test_cnot_arbitrary_positions():
    q = QuantumState(3, initial_state=4)  # |100>, q2=1
    q.cnot(2, 0)
    assert np.argmax(np.abs(q.statevector())) == 5  # |101>


def test_cz_preserves_probabilities_and_changes_phase():
    q = QuantumState(2).h(0).h(1)
    before = q.statevector().copy()
    q.cz(0, 1)
    assert np.allclose(np.abs(before), np.abs(q.statevector()))
    assert np.isclose(q.statevector()[3], -0.5)


def test_swap():
    q = QuantumState(2, initial_state=1)
    q.swap(0, 1)
    assert np.argmax(np.abs(q.statevector())) == 2


def test_measure_collapses_state():
    q = QuantumState(1).x(0)
    result = q.measure(seed=1)
    assert result.outcome == 1
    assert np.allclose(q.statevector(), [0, 1])


def test_invalid_inputs():
    with pytest.raises(ValueError):
        QuantumState(0)
    with pytest.raises(ValueError):
        QuantumState(MAX := 21)
    with pytest.raises(ValueError):
        QuantumState(2, initial_state=4)
    with pytest.raises(ValueError):
        QuantumState(2).h(2)
    with pytest.raises(ValueError):
        QuantumState(2).cnot(0, 0)
