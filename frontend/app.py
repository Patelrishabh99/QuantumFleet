# frontend/streamlit_app.py
import streamlit as st
import requests, time, json, io
from streamlit_folium import st_folium
import folium

API = "http://127.0.0.1:8000"
st.set_page_config(layout="wide", page_title="QuantumFleet UI")
st.title("QuantumFleet — Fleet Optimization (OR-Tools & Hybrid)")

if "depot" not in st.session_state: st.session_state.depot = None
if "orders" not in st.session_state: st.session_state.orders = []  # list of dicts
if "vehicles" not in st.session_state: st.session_state.vehicles = []  # list of dicts

# Sidebar controls
with st.sidebar:
    st.header("Scenario Controls")
    nveh = st.number_input("Number of vehicles", 1, 10, value=3)
    cap = st.number_input("Vehicle capacity", 1, 1000, value=50)
    solver = st.selectbox("Solver", ["OR-Tools (Classical)", "Hybrid (Quantum-inspired)"])
    cluster_k = st.number_input("Hybrid clusters (k)", 1, 10, value=nveh)
    if st.button("Clear scenario"):
        requests.post(f"{API}/clear")
        st.session_state.depot = None
        st.session_state.orders = []
        st.session_state.vehicles = []
        st.experimental_rerun()

# Map to set depot/orders
st.subheader("Map: Click to set DEPOT (first) then add ORDERS")
center = st.session_state.depot or [20.5937, 78.9629]
m = folium.Map(location=center, zoom_start=6)
if st.session_state.depot:
    folium.Marker(st.session_state.depot, tooltip="Depot", icon=folium.Icon(color="blue")).add_to(m)
for i,o in enumerate(st.session_state.orders, start=1):
    folium.Marker([o["lat"], o["lon"]], tooltip=f"Order {i} d={o['demand']}", icon=folium.Icon(color="green")).add_to(m)
click = st_folium(m, width=900, height=520)

if click and click.get("last_clicked"):
    lat = float(click["last_clicked"]["lat"]); lon = float(click["last_clicked"]["lng"])
    if st.session_state.depot is None:
        st.session_state.depot = [lat, lon]; st.success("Depot placed")
        requests.post(f"{API}/depot", json={"lat": lat, "lon": lon})
        # create initial vehicles (all starting at depot)
        v_list = [{"id": f"v{i+1}", "start_lat": lat, "start_lon": lon, "capacity": int(cap)} for i in range(int(nveh))]
        st.session_state.vehicles = v_list
        requests.post(f"{API}/vehicles", json=v_list)
    else:
        # add order with minimal form
        demand = st.number_input("Demand for this order", min_value=1, max_value=1000, value=1, key=f"d_{len(st.session_state.orders)}")
        priority = st.selectbox("Priority", ["low","normal","high"], index=1, key=f"p_{len(st.session_state.orders)}")
        if st.button("Add order at clicked location", key=f"add_{len(st.session_state.orders)}"):
            o = {"id": f"o{len(st.session_state.orders)+1}", "lat": lat, "lon": lon, "demand": int(demand), "priority": priority}
            st.session_state.orders.append(o)
            requests.post(f"{API}/orders", json=st.session_state.orders)  # push full orders list
            st.success("Order added")

st.divider()

colA, colB = st.columns([2,1])
with colB:
    st.subheader("Scenario Summary")
    st.write("Depot:", st.session_state.depot)
    st.write("Orders:", len(st.session_state.orders))
    st.write("Vehicles:", nveh, "capacity:", cap)
    if st.button("Send current scenario to backend"):
        # ensure vehicles updated to start at depot
        if st.session_state.depot is None:
            st.error("Place depot first")
        else:
            v_list = [{"id": f"v{i+1}", "start_lat": st.session_state.depot[0], "start_lon": st.session_state.depot[1], "capacity": int(cap)} for i in range(int(nveh))]
            st.session_state.vehicles = v_list
            r1 = requests.post(f"{API}/vehicles", json=v_list)
            r2 = requests.post(f"{API}/orders", json=st.session_state.orders)
            st.write("Vehicles:", r1.status_code, "Orders:", r2.status_code)

with colA:
    st.subheader("Optimize")
    chosen = "ortools" if solver.startswith("OR-Tools") else "hybrid"
    if st.button("🚀 Optimize now"):
        # ensure backend has depot/vehicles/orders
        if st.session_state.depot is None or len(st.session_state.orders) == 0:
            st.error("Place depot and at least one order")
        else:
            # send vehicles+orders again to be safe
            v_list = [
                {"id": f"v{i + 1}", "start_lat": st.session_state.depot[0], "start_lon": st.session_state.depot[1],
                 "capacity": int(cap)} for i in range(int(nveh))]

            requests.post(f"{API}/vehicles", json=v_list)
            requests.post(f"{API}/orders", json=st.session_state.orders)

            with st.spinner("Solving..."):
                r = requests.post(f"{API}/optimize", params={"solver": chosen, "cluster_k": int(cluster_k)})
                if r.status_code != 200:
                    st.error(f"Optimize failed: {r.text}")
                else:
                    res = r.json()
                    # Save results in session_state so they persist
                    st.session_state["last_solution"] = res

    # 👉 Render results if available
    if "last_solution" in st.session_state:
        res = st.session_state["last_solution"]
        routes = res.get("routes_coords", [])
        dist = res.get("distance_m", 0)

        st.success(f"Solved. distance(m): {dist}")

        # draw map with colored routes
        mm = folium.Map(location=st.session_state.depot, zoom_start=10)
        folium.Marker(st.session_state.depot, tooltip="Depot", icon=folium.Icon(color="blue")).add_to(mm)
        palette = ["red", "blue", "green", "purple", "orange", "darkred", "cadetblue"]
        for i, route in enumerate(routes):
            if not route: continue
            folium.PolyLine(route, color=palette[i % len(palette)], weight=5, tooltip=f"Vehicle v{i + 1}").add_to(mm)
            for j, p in enumerate(route):
                folium.CircleMarker(p, radius=4, color=palette[i % len(palette)], fill=True).add_to(mm)
        st_folium(mm, width=900, height=520)

        # per-vehicle table
        summary = []
        for i, route in enumerate(routes):
            summary.append({"vehicle": f"v{i + 1}", "stops": max(0, len(route) - 1)})
        st.dataframe(summary)
