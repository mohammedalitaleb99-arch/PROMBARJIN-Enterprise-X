"""PROMBARJIN Ω Quantum Core — local state-vector simulator.

Convention: q0 is the least-significant bit (LSB).
This is a classical simulation of quantum logic; no quantum hardware is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np

MAX_QUBITS = 20

X = np.array([[0, 1], [1, 0]], dtype=np.complex128)
Y = np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
Z = np.array([[1, 0], [0, -1]], dtype=np.complex128)
H = np.array([[1, 1], [1, -1]], dtype=np.complex128) / np.sqrt(2.0)
S = np.array([[1, 0], [0, 1j]], dtype=np.complex128)
T = np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=np.complex128)


def rx(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=np.complex128)


def ry(theta: float) -> np.ndarray:
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)


def rz(theta: float) -> np.ndarray:
    return np.array(
        [[np.exp(-1j * theta / 2), 0], [0, np.exp(1j * theta / 2)]],
        dtype=np.complex128,
    )


@dataclass(frozen=True)
class MeasurementResult:
    outcome: int
    bitstring: str


class QuantumState:
    """Small, correctness-first state-vector simulator."""

    def __init__(self, num_qubits: int, initial_state: int = 0, max_qubits: int = MAX_QUBITS):
        if not isinstance(num_qubits, int) or num_qubits < 1:
            raise ValueError("num_qubits must be a positive integer")
        if num_qubits > max_qubits:
            raise ValueError(f"num_qubits {num_qubits} exceeds configured maximum {max_qubits}")
        max_initial = (1 << num_qubits) - 1
        if not isinstance(initial_state, int) or not (0 <= initial_state <= max_initial):
            raise ValueError(f"initial_state must be in [0, {max_initial}]")
        self.num_qubits = num_qubits
        self.max_qubits = max_qubits
        self.dim = 1 << num_qubits
        self.state = np.zeros(self.dim, dtype=np.complex128)
        self.state[initial_state] = 1.0 + 0.0j

    def _check_qubit(self, q: int) -> None:
        if not isinstance(q, int) or not (0 <= q < self.num_qubits):
            raise ValueError(f"Qubit index {q} out of range [0, {self.num_qubits - 1}]")

    def _check_pair(self, q1: int, q2: int) -> None:
        self._check_qubit(q1)
        self._check_qubit(q2)
        if q1 == q2:
            raise ValueError("Qubit indices must be different")

    @staticmethod
    def _validate_gate(gate: np.ndarray) -> np.ndarray:
        gate = np.asarray(gate, dtype=np.complex128)
        if gate.shape != (2, 2):
            raise ValueError("Single-qubit gate must have shape (2, 2)")
        if not np.allclose(gate.conj().T @ gate, np.eye(2), atol=1e-12):
            raise ValueError("Gate must be unitary")
        return gate

    def _apply_single(self, gate: np.ndarray, target: int) -> "QuantumState":
        self._check_qubit(target)
        g = self._validate_gate(gate)
        bit = 1 << target
        for base in range(self.dim):
            if base & bit:
                continue
            partner = base | bit
            a0, a1 = self.state[base], self.state[partner]
            self.state[base] = g[0, 0] * a0 + g[0, 1] * a1
            self.state[partner] = g[1, 0] * a0 + g[1, 1] * a1
        return self

    def x(self, q: int) -> "QuantumState": return self._apply_single(X, q)
    def y(self, q: int) -> "QuantumState": return self._apply_single(Y, q)
    def z(self, q: int) -> "QuantumState": return self._apply_single(Z, q)
    def h(self, q: int) -> "QuantumState": return self._apply_single(H, q)
    def s(self, q: int) -> "QuantumState": return self._apply_single(S, q)
    def t(self, q: int) -> "QuantumState": return self._apply_single(T, q)
    def rx(self, q: int, theta: float) -> "QuantumState": return self._apply_single(rx(theta), q)
    def ry(self, q: int, theta: float) -> "QuantumState": return self._apply_single(ry(theta), q)
    def rz(self, q: int, theta: float) -> "QuantumState": return self._apply_single(rz(theta), q)

    def cnot(self, control: int, target: int) -> "QuantumState":
        self._check_pair(control, target)
        cbit, tbit = 1 << control, 1 << target
        for basis in range(self.dim):
            if basis & cbit:
                partner = basis ^ tbit
                if partner > basis:
                    self.state[basis], self.state[partner] = self.state[partner], self.state[basis]
        return self

    def cz(self, q1: int, q2: int) -> "QuantumState":
        self._check_pair(q1, q2)
        b1, b2 = 1 << q1, 1 << q2
        mask = b1 | b2
        for basis in range(self.dim):
            if (basis & mask) == mask:
                self.state[basis] *= -1
        return self

    def swap(self, q1: int, q2: int) -> "QuantumState":
        self._check_pair(q1, q2)
        b1, b2 = 1 << q1, 1 << q2
        for basis in range(self.dim):
            x1, x2 = basis & b1, basis & b2
            if bool(x1) == bool(x2):
                continue
            partner = basis ^ b1 ^ b2
            if partner > basis:
                self.state[basis], self.state[partner] = self.state[partner], self.state[basis]
        return self

    def probabilities(self) -> np.ndarray:
        probs = np.abs(self.state) ** 2
        total = float(probs.sum())
        if not np.isfinite(total) or total <= 0:
            raise RuntimeError("Statevector has invalid norm")
        return probs / total

    def basis_probabilities(self, threshold: float = 1e-15) -> Dict[str, float]:
        probs = self.probabilities()
        out: Dict[str, float] = {}
        for i, p in enumerate(probs):
            p = float(p.real)
            if p > threshold:
                out[format(i, f"0{self.num_qubits}b")] = p
        return out

    def sample(self, shots: int = 1024, seed: Optional[int] = None) -> List[int]:
        if not isinstance(shots, int) or shots < 1:
            raise ValueError("shots must be a positive integer")
        rng = np.random.default_rng(seed)
        return rng.choice(self.dim, size=shots, p=self.probabilities()).tolist()

    def measure(self, seed: Optional[int] = None) -> MeasurementResult:
        rng = np.random.default_rng(seed)
        outcome = int(rng.choice(self.dim, p=self.probabilities()))
        self.state.fill(0)
        self.state[outcome] = 1.0 + 0.0j
        return MeasurementResult(outcome, format(outcome, f"0{self.num_qubits}b"))

    def is_normalized(self, atol: float = 1e-12) -> bool:
        return bool(np.isclose(np.sum(np.abs(self.state) ** 2), 1.0, atol=atol))

    def statevector(self) -> np.ndarray:
        return self.state.copy()

    @classmethod
    def bell_state(cls) -> "QuantumState":
        state = cls(2)
        return state.h(0).cnot(0, 1)

    @classmethod
    def ghz_state(cls, num_qubits: int = 3) -> "QuantumState":
        state = cls(num_qubits)
        state.h(0)
        for q in range(1, num_qubits):
            state.cnot(0, q)
        return state
