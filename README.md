# battery-prediction

Battery degradation and cycle-life prediction. Generates simulation job manifests from config-driven sweeps.

## Quick start

**Enter the dev container (shell):**
```bash
make docker
# or: docker compose run --rm app
```

**Run the sweep** (build jobs from `configs/sweep.yaml`, writes to `data/<run_id>/jobs/jobs.parquet`):
```bash
make docker-sweep
# or: docker compose run --rm app python -m bdt.sim.sweep configs/sweep.yaml
```

## Project layout

- `bdt/` — Python package: `bdt.data.schema` (job schema), `bdt.sim.sweep` (config → job manifest).
- `configs/sweep.yaml` — Sweep config (run id, seed, model, n_cycles, c_rates, temperatures, DoD, rest, param noise).
- `data/` — Output directory; each run gets `data/<run_id>/jobs/jobs.parquet`.

## Requirements

- Docker and Docker Compose (or run locally with Python 3.12+ and deps from `requirements.txt`).
