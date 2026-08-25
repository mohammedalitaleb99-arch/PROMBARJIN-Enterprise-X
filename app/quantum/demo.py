"""Small Quantum Intelligence demo used by the mobile/web UI."""
from .core import QuantumState


def bell_demo(shots: int = 1024, seed: int | None = 42) -> dict:
    state = QuantumState.bell_state()
    samples = state.sample(shots=shots, seed=seed)
    counts = {}
    for value in samples:
        key = format(value, f"0{state.num_qubits}b")
        counts[key] = counts.get(key, 0) + 1
    return {
        "backend": "local_state_vector_simulator",
        "label": "CLASSICAL SIMULATION OF QUANTUM LOGIC",
        "num_qubits": state.num_qubits,
        "shots": shots,
        "probabilities": state.basis_probabilities(),
        "counts": counts,
    }


def ghz_demo(num_qubits: int = 3, shots: int = 1024, seed: int | None = 42) -> dict:
    state = QuantumState.ghz_state(num_qubits)
    samples = state.sample(shots=shots, seed=seed)
    counts = {}
    for value in samples:
        key = format(value, f"0{num_qubits}b")
        counts[key] = counts.get(key, 0) + 1
    return {
        "backend": "local_state_vector_simulator",
        "label": "CLASSICAL SIMULATION OF QUANTUM LOGIC",
        "num_qubits": num_qubits,
        "shots": shots,
        "probabilities": state.basis_probabilities(),
        "counts": counts,
    }
