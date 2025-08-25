# app/models.py
from typing import List, Dict

# In-memory stores (MVP)
DEPOT = None  # dict: {"lat":..., "lon":...}
VEHICLES: List[Dict] = []  # each: {"id": str, "start_lat":..., "start_lon":..., "capacity": int}
ORDERS: List[Dict] = []    # each: {"id": str, "lat":..., "lon":..., "demand": int, "priority": str}

def set_depot(lat: float, lon: float):
    global DEPOT
    DEPOT = {"lat": float(lat), "lon": float(lon)}

def get_depot():
    return DEPOT

def save_vehicles(vehicles: List[Dict]):
    global VEHICLES
    VEHICLES = vehicles

def get_vehicles():
    return VEHICLES

def save_orders(orders: List[Dict]):
    global ORDERS
    ORDERS = orders

def get_orders():
    return ORDERS

def clear_all():
    global DEPOT, VEHICLES, ORDERS
    DEPOT = None; VEHICLES = []; ORDERS = []
