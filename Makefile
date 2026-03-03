docker:
	docker compose run --rm app

docker-sweep:
	docker compose run --rm app python -m bdt.sim.sweep configs/sweep.yaml