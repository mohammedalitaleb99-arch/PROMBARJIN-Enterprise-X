from fastapi import APIRouter
from .demo import bell_demo, ghz_demo

router = APIRouter(prefix="/api/quantum", tags=["quantum"])

@router.get("/health")
def health():
    return {"status":"online","backend":"local_state_vector_simulator","label":"CLASSICAL SIMULATION OF QUANTUM LOGIC","hardware":False,"quantum_advantage":False}

@router.get("/bell")
def bell(shots:int=1024):
    return bell_demo(shots)

@router.get("/ghz")
def ghz(qubits:int=3, shots:int=1024):
    return ghz_demo(qubits, shots)
