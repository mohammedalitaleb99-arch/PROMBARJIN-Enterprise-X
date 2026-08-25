from fastapi import APIRouter, HTTPException
from .demo import bell_demo, ghz_demo

router = APIRouter(prefix="/api/quantum", tags=["quantum"])

@router.get("/health")
def quantum_health() -> dict:
    return {"status": "online", "backend": "local_state_vector_simulator", "label": "CLASSICAL SIMULATION OF QUANTUM LOGIC", "hardware": False, "quantum_advantage": False}

@router.get("/bell")
def quantum_bell(shots: int = 1024) -> dict:
    if not 1 <= shots <= 100000:
        raise HTTPException(status_code=400, detail="shots must be between 1 and 100000")
    return bell_demo(shots=shots)

@router.get("/ghz")
def quantum_ghz(qubits: int = 3, shots: int = 1024) -> dict:
    if not 2 <= qubits <= 20:
        raise HTTPException(status_code=400, detail="qubits must be between 2 and 20")
    if not 1 <= shots <= 100000:
        raise HTTPException(status_code=400, detail="shots must be between 1 and 100000")
    return ghz_demo(num_qubits=qubits, shots=shots)
