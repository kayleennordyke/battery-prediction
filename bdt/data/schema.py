# bdt/data/schema.py
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Tuple
import json
import hashlib


def stable_hash(obj: Any) -> str:
    """Stable short hash for dict-like objects (order-independent via sorted keys)."""
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


@dataclass(frozen=True)
class SimJob:
    """
    One independent simulation task.
    Everything needed to run one PyBaMM simulation should be representable here.
    """
    run_id: str
    cell_id: int
    protocol_id: str
    model: str
    n_cycles: int
    temperature_C: float
    c_rate: float
    dod_min: float
    dod_max: float
    rest_minutes: int
    params: Dict[str, Any]          # parameter overrides / perturbations
    seed: int

    @property
    def job_id(self) -> str:
        payload = {
            "run_id": self.run_id,
            "cell_id": self.cell_id,
            "protocol_id": self.protocol_id,
            "model": self.model,
            "n_cycles": self.n_cycles,
            "temperature_C": self.temperature_C,
            "c_rate": self.c_rate,
            "dod": [self.dod_min, self.dod_max],
            "rest_minutes": self.rest_minutes,
            "params": self.params,
            "seed": self.seed,
        }
        return stable_hash(payload)

    def to_row(self) -> Dict[str, Any]:
        row = asdict(self)
        row["job_id"] = self.job_id
        # Store dict fields as JSON strings for Parquet friendliness
        row["params_json"] = json.dumps(self.params, sort_keys=True)
        del row["params"]
        return row


def protocol_id(c_rate: float, temp_c: float, dod: Tuple[float, float], rest_min: int) -> str:
    """Human-readable protocol ID used for grouping/splits."""
    return f"Cr{c_rate:g}_T{temp_c:g}_DoD{dod[0]:.2f}-{dod[1]:.2f}_R{rest_min:d}"