# app/main.py
from fastapi import FastAPI, HTTPException
from typing import List, Dict
from pydantic import BaseModel
from app.models import set_depot, get_depot, save_vehicles, get_vehicles, save_orders, get_orders, clear_all
from app.vrp_solver import solve_vrp
from app.quantum_poc import hybrid_optimize_cluster

app = FastAPI(title="QuantumFleet API")

# Pydantic models for request validation
class DepotIn(BaseModel):
    lat: float
    lon: float

class VehicleIn(BaseModel):
    id: str
    start_lat: float
    start_lon: float
    capacity: int = 100

class OrderIn(BaseModel):
    id: str
    lat: float
    lon: float
    demand: int = 1
    priority: str = "normal"

@app.post("/clear")
def api_clear():
    clear_all()
    return {"status":"cleared"}

@app.post("/depot")
def api_set_depot(d: DepotIn):
    set_depot(d.lat, d.lon)
    return {"status":"ok", "depot": {"lat": d.lat, "lon": d.lon}}

@app.post("/vehicles")
def api_vehicles(vehicles: List[VehicleIn]):
    save_vehicles([v.dict() for v in vehicles])
    return {"status":"ok", "count": len(vehicles)}

@app.post("/orders")
def api_orders(orders: List[OrderIn]):
    save_orders([o.dict() for o in orders])
    return {"status":"ok", "count": len(orders)}

@app.post("/optimize")
def api_optimize(solver: str = "ortools", cluster_k: int = 3):
    depot = get_depot()
    vehicles = get_vehicles()
    orders = get_orders()
    if not depot:
        raise HTTPException(status_code=400, detail="Depot required")
    if not vehicles:
        raise HTTPException(status_code=400, detail="At least one vehicle required")
    if not orders:
        raise HTTPException(status_code=400, detail="At least one order required")

    # Build minimal vehicle & orders cleaned lists
    veh_list = vehicles
    orders_list = orders

    if solver == "ortools":
        res = solve_vrp(veh_list, orders_list, depot)
        # Build human-friendly lat/lon routes as well
        coords = res.get("coords", [])
        routes_idx = res.get("routes", [])
        routes_coords = []
        for route in routes_idx:
            routes_coords.append([[coords[n][0], coords[n][1]] for n in route])
        return {"coords": coords, "routes_idx": routes_idx, "routes_coords": routes_coords, "distance_m": res.get("distance"), "meta": res.get("meta", {})}
    else:
        # hybrid expects orders as list of tuples
        orders_tuples = [(o["lat"], o["lon"]) for o in orders_list]
        res = hybrid_optimize_cluster(k=cluster_k, depot=(depot["lat"], depot["lon"]), orders=orders_tuples)
        coords = res.get("coords", [])
        routes_idx = res.get("routes", [])
        routes_coords = []
        for route in routes_idx:
            routes_coords.append([[coords[n][0], coords[n][1]] for n in route])
        return {"coords": coords, "routes_idx": routes_idx, "routes_coords": routes_coords, "distance_m": res.get("distance"), "meta": res.get("meta", {})}
