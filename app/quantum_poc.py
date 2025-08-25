# app/quantum_poc.py
from app.preprocessor import cluster_coords, distance_matrix
import numpy as np
from typing import List, Dict, Tuple

def _nn_tsp_order(coords: List[Tuple[float,float]]):
    n = len(coords)
    if n <= 1:
        return list(range(n))
    dist = distance_matrix(coords)
    visited = {0}
    order = [0]
    cur = 0
    while len(visited) < n:
        nxt = min([ (dist[cur,j], j) for j in range(n) if j not in visited ])[1]
        visited.add(nxt); order.append(int(nxt)); cur = nxt
    return order

def hybrid_optimize_cluster(k: int, depot: Tuple[float,float], orders: List[Tuple[float,float]]):
    """
    orders: list of (lat,lon)
    returns same shape as VRP solver: coords, routes, distance (meters)
    """
    if not orders:
        return {"coords": [depot], "routes": [], "distance": 0, "meta": {"msg":"no_orders"}}
    coords = [depot] + list(orders)
    clusters = cluster_coords(orders, k=k if k>0 else 1)
    routes = []
    total_m = 0
    for _, idxs in clusters.items():
        if not idxs:
            routes.append([0]); continue
        local_coords = [depot] + [orders[i] for i in idxs]
        perm = _nn_tsp_order(local_coords)
        # map to global indices
        global_route = []
        for li in perm:
            if li == 0:
                global_route.append(0)
            else:
                global_route.append(1 + idxs[li-1])
        # length
        poly = [coords[i] for i in global_route]
        # pairwise haversine
        for i in range(len(poly)-1):
            a=poly[i]; b=poly[i+1]
            # simple haversine (km) -> m
            from math import radians, sin, cos, asin, sqrt
            R=6371
            lon1, lat1, lon2, lat2 = map(radians,[a[1],a[0],b[1],b[0]])
            dlat=lat2-lat1; dlon=lon2-lon1
            aa = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
            km = 2*R*asin(sqrt(aa))
            total_m += km*1000
        routes.append(global_route)
    return {"coords": coords, "routes": routes, "distance": int(total_m), "meta": {"solver":"hybrid"}}
