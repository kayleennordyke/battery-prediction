from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple
import itertools
import yaml
import numpy as np
import pandas as pd

from bdt.data.schema import SimJob, protocol_id


def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_jobs(cfg: Dict[str, Any]) -> List[SimJob]:
    run_id = cfg["run"]["run_id"]
    seed = int(cfg["run"]["seed"])
    rng = np.random.default_rng(seed)

    model = cfg["sim"]["model"]
    n_cycles = int(cfg["sim"]["n_cycles"])

    n_cells = int(cfg["sweep"]["n_cells"])
    c_rates = cfg["sweep"]["c_rates"]
    temps = cfg["sweep"]["temperatures_C"]
    dods: List[Tuple[float, float]] = [tuple(x) for x in cfg["sweep"]["dod_windows"]]
    rests = cfg["sweep"]["rest_minutes"]

    noise_cfg = cfg["sweep"]["param_noise"]
    noise_enabled = bool(noise_cfg.get("enabled", False))
    sigma = float(noise_cfg.get("sigma_frac", 0.0))
    keys = list(noise_cfg.get("keys", []))

    # Define protocol grid once; then assign across cells (balanced-ish)
    protocol_grid = list(itertools.product(c_rates, temps, dods, rests))

    jobs: List[SimJob] = []
    for cell_id in range(n_cells):
        # Assign a protocol (round-robin) so all combos are represented
        c_rate, temp_c, dod, rest_min = protocol_grid[cell_id % len(protocol_grid)]
        pid = protocol_id(c_rate, temp_c, dod, rest_min)

        params: Dict[str, Any] = {}
        if noise_enabled and keys and sigma > 0:
            # multiplicative noise: p -> p*(1+eps)
            for k in keys:
                eps = rng.normal(loc=0.0, scale=sigma)
                params[k] = 1.0 + float(eps)  # store multiplier for now (map later)

        job = SimJob(
            run_id=run_id,
            cell_id=cell_id,
            protocol_id=pid,
            model=model,
            n_cycles=n_cycles,
            temperature_C=float(temp_c),
            c_rate=float(c_rate),
            dod_min=float(dod[0]),
            dod_max=float(dod[1]),
            rest_minutes=int(rest_min),
            params=params,
            seed=seed + cell_id,  # deterministic per cell
        )
        jobs.append(job)

    return jobs


def write_jobs(jobs: List[SimJob], out_path: str | Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame([j.to_row() for j in jobs])
    df.to_parquet(out_path, index=False)
    return out_path


def main(config_path: str = "configs/sweep.yaml") -> None:
    cfg = load_yaml(config_path)

    out_dir = Path(cfg["run"]["out_dir"])
    jobs_rel = cfg["output"]["jobs_path"]
    jobs_path = out_dir / cfg["run"]["run_id"] / jobs_rel

    jobs = build_jobs(cfg)
    p = write_jobs(jobs, jobs_path)

    print(f"Wrote {len(jobs)} jobs -> {p}")


if __name__ == "__main__":
    main()