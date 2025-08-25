# app/vrp_solver.py
import math
from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from typing import List, Dict, Tuple

def haversine_km(a: Tuple[float,float], b: Tuple[float,float]) -> float:
    from math import radians, sin, cos, asin, sqrt
    lat1, lon1 = a; lat2, lon2 = b
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    la1 = radians(lat1); la2 = radians(lat2)
    a_ = sin(dlat/2)**2 + cos(la1)*cos(la2)*sin(dlon/2)**2
    return 6371 * 2 * asin(math.sqrt(a_))

def build_distance_matrix(coords: List[Tuple[float,float]]) -> List[List[int]]:
    n = len(coords)
    mat = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                mat[i][j] = 0
            else:
                mat[i][j] = int(haversine_km(coords[i], coords[j]) * 1000)  # meters
    return mat

def solve_vrp(vehicles: List[Dict], orders: List[Dict], depot: Dict, time_limit_seconds: int = 15):
    """
    vehicles: list of dict {id, start_lat, start_lon, capacity}
    orders: list of dict {id, lat, lon, demand}
    depot: {lat, lon}
    Returns:
      {"coords": [(lat,lon), ...], "routes": [[node_idx,...], ...], "distance": total_meters}
      coords[0] == depot; order nodes 1..N
    """
    if not depot or not orders or not vehicles:
        return {"coords": [], "routes": [], "distance": 0, "meta": {"msg":"need depot/vehicles/orders"}}

    # build coords: depot first, then orders
    coords = [(float(depot["lat"]), float(depot["lon"]))] + [(float(o["lat"]), float(o["lon"])) for o in orders]
    demands = [0] + [int(o.get("demand", 1)) for o in orders]
    vehicle_caps = [int(v.get("capacity", 100)) for v in vehicles]
    num_vehicles = len(vehicle_caps)

    dist_mat = build_distance_matrix(coords)

    manager = pywrapcp.RoutingIndexManager(len(dist_mat), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_mat[from_node][to_node]

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    # capacity constraint
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]
    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, vehicle_caps, True, "Capacity")

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_params.time_limit.FromSeconds(time_limit_seconds)

    solution = routing.SolveWithParameters(search_params)
    if not solution:
        return {"coords": coords, "routes": [], "distance": None, "meta": {"msg":"no_solution"}}

    routes = []
    total_m = 0
    for v in range(num_vehicles):
        idx = routing.Start(v)
        route_nodes = []
        prev_index = idx
        while not routing.IsEnd(idx):
            node = manager.IndexToNode(idx)
            route_nodes.append(node)  # node index in coords
            next_index = solution.Value(routing.NextVar(idx))
            total_m += routing.GetArcCostForVehicle(idx, next_index, v)
            idx = next_index
        # Optionally append end depot index if you want closed route
        # route_nodes.append(0)
        routes.append(route_nodes)

    return {"coords": coords, "routes": routes, "distance": int(total_m), "meta": {"solver":"ortools"}}
