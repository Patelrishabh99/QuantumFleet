<<<<<<< HEAD
# Quantum Path Planner — Starter Project

This is an MVP implementation of the Quantum Path Planner (QPP). It includes:
- FastAPI backend exposing endpoints to ingest orders/vehicles and run optimization jobs.
- OR-Tools CVRP example solver (production core).
- Preprocessor for clustering and distance matrix (Haversine).
- Quantum POC: QUBO mapping and a simulated annealing stub — replaceable with D-Wave or Qiskit calls.
- Simple SQLite persistence for jobs (MVP).

## Run locally (quick)
1. Create venv: `python -m venv venv && source venv/bin/activate`
2. Install: `pip install -r requirements.txt`
3. Run server: `bash scripts/run_local.sh`
4. Endpoints:
   - POST /orders  (body: list of orders)
   - POST /vehicles (body: list of vehicles)
   - POST /optimize (?solver=ortools|hybrid&cluster_k=N) -> returns job_id
   - GET /jobs/{job_id}

See `app/` for code files.
=======
# QuantumFleet
###AVQH
>>>>>>> feed1386bd4676b2802f41c5e1e02eb2fc2789fb
