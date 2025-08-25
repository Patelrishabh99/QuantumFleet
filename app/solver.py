from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from app.preprocessor import distance_matrix
from app.models import get_orders, get_vehicles

def solve_vrp():
    # Load orders/vehicles from in-memory MVP storage
    orders = get_orders()
    vehicles = get_vehicles()
    if not orders:
        return {'routes': [], 'distance': 0, 'msg': 'no orders'}

    # Depot = first vehicle start (or first order if no vehicle provided)
    depot = (vehicles[0]['start_lat'], vehicles[0]['start_lon']) if vehicles else (orders[0]['lat'], orders[0]['lon'])
    coords = [depot] + [(o['lat'], o['lon']) for o in orders]
    demands = [0] + [o.get('demand',1) for o in orders]
    vehicle_capacities = [v.get('capacity',100) for v in vehicles] if vehicles else [100,100]
    num_vehicles = len(vehicle_capacities)

    dist_mat = (distance_matrix(coords) * 1000).astype(int).tolist()  # meters int

    manager = pywrapcp.RoutingIndexManager(len(dist_mat), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return dist_mat[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Capacity constraints
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(demand_callback_index, 0, vehicle_capacities, True, 'Capacity')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.time_limit.FromSeconds(10)

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        routes = []
        total_distance = 0
        for v in range(num_vehicles):
            idx = routing.Start(v)
            route = []
            route_dist = 0
            while not routing.IsEnd(idx):
                node = manager.IndexToNode(idx)
                route.append(node)
                previous_index = idx
                idx = solution.Value(routing.NextVar(idx))
                route_dist += routing.GetArcCostForVehicle(previous_index, idx, v)
            routes.append(route)
            total_distance += route_dist
        result = {'routes': routes, 'distance': int(total_distance), 'coords': coords}
    else:
        result = {'routes': [], 'distance': None, 'msg': 'no_solution'}
    return result
