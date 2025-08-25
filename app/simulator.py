from app.solver import solve_vrp
from app.models import init_db, save_orders, save_vehicles

def run_scenario():
    init_db()
    orders = [
        {"id": "o1", "lat": 12.98, "lon": 77.58, "demand": 1},
        {"id": "o2", "lat": 12.96, "lon": 77.60, "demand": 1},
        {"id": "o3", "lat": 12.99, "lon": 77.57, "demand": 1},
    ]
    vehicles = [
        {"id": "v1", "start_lat": 12.97, "start_lon": 77.59, "capacity": 3}
    ]
    save_orders([type('O', (), o)() for o in orders])
    save_vehicles([type('V', (), v)() for v in vehicles])
    res = solve_vrp()
    print('Simulation result:', res)

if __name__ == '__main__':
    run_scenario()
