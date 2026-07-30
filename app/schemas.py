from pydantic import BaseModel
from typing import Dict, List

class SimulationRequest(BaseModel):
    scenario: str
    parameters: Dict

class SimulationResponse(BaseModel):
    result: Dict

class SweepRequest(BaseModel):
    scenario: str
    parameters: Dict
    sample_sizes: List[int]

class SweepResponse(BaseModel):
    points: List[Dict]