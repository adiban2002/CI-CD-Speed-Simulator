import csv
import os
import random
from typing import List, Dict

from simulator.strategy import (
    # Build
    sequential_build,
    parallel_build,
    cached_build,
    slim_image_build,

    # Load Balancing
    round_robin_load,
    least_connections_load,
    random_load,
    genetic_algorithm_load,
    irb_load,
    rrb_load,
    iot_lb_load,
    tl_lb_load,

    # Scheduling
    fcfs_scheduling,
    sjf_scheduling,
    srtf_scheduling,
    hrrn_scheduling,
)

# =================================================
# CSV LOGGING
# =================================================

os.makedirs("logs", exist_ok=True)
LOG_FILE = os.path.join("logs", "results.csv")

CSV_HEADERS = [
    "phase", "strategy", "algorithm",
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response",
]

def save_results(data: Dict):
    exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not exists:
            writer.writeheader()
        writer.writerow({k: data.get(k, "") for k in CSV_HEADERS})

# =================================================
# INPUT HELPERS
# =================================================

def _read_int(prompt: str, default: int = None) -> int:
    while True:
        try:
            s = input(prompt)
            if s == "" and default is not None:
                return default
            return int(s)
        except ValueError:
            print("Enter a valid integer.")

def _read_float(prompt: str, default: float = None) -> float:
    while True:
        try:
            s = input(prompt)
            if s == "" and default is not None:
                return default
            return float(s)
        except ValueError:
            print("Enter a valid number.")

# =================================================
# BUILD PHASE
# =================================================

def build_phase():
    print("\n--- CI/CD Build Simulator ---\n")
    n = _read_int("Enter number of services: ")
    t = _read_int("Enter avg build time per service (minutes): ")

    print("\n1. Sequential\n2. Parallel\n3. Cached\n4. Slim Image")
    c = _read_int("Choice: ")

    if c == 1:
        r = sequential_build(n, t)
    elif c == 2:
        r = parallel_build(n, t)
    elif c == 3:
        changed = _read_int("Changed services: ", 0)
        r = cached_build(n, t, changed)
    elif c == 4:
        factor = _read_float("Slim factor (0.7): ", 0.7)
        r = slim_image_build(n, t, factor)
    else:
        return

    print(f"\n{r['strategy']} | Time={r['total_time']} | Speedup={r['speedup']}")
    save_results({
        "phase": "Build",
        "strategy": r["strategy"],
        "total_time": r["total_time"],
        "speedup": r["speedup"],
        "efficiency": r["efficiency"]
    })

# =================================================
# LOAD BALANCING PHASE
# =================================================

def _collect_service_caps(n: int) -> List[Dict[str, float]]:
    print("\nIRB Capacities (Enter = default, Ctrl+C = auto)")
    caps = []
    try:
        for i in range(n):
            print(f"\nInstance {i}")
            caps.append({
                "cpu_capacity": _read_float(" CPU cap (10): ", 10),
                "mem_capacity": _read_float(" MEM cap (8): ", 8),
                "cpu_cost": _read_float(" CPU cost (1): ", 1),
                "mem_cost": _read_float(" MEM cost (1): ", 1),
            })
    except KeyboardInterrupt:
        print("\n⚠️ Using default capacities for all instances.")
        caps = [{"cpu_capacity":10,"mem_capacity":8,"cpu_cost":1,"mem_cost":1} for _ in range(n)]
    return caps

def _collect_iot_signals(n: int) -> List[Dict[str, float]]:
    print("\nIoT Signals (Ctrl+C = auto/default)")
    signals = []
    try:
        for i in range(n):
            print(f"\nInstance {i}")
            signals.append({
                "latency": _read_float(" Latency ms (50): ", 50),
                "network_delay": _read_float(" Network delay ms (20): ", 20),
                "cpu_temp": _read_float(" CPU temp °C (65): ", 65),
            })
    except KeyboardInterrupt:
        print("\n⚠️ Using default IoT signals.")
        signals = [{"latency":50,"network_delay":20,"cpu_temp":65} for _ in range(n)]
    return signals

def load_balancing_phase():
    print("\n--- Load Balancing ---\n")
    n = _read_int("Services: ")
    r = _read_int("Requests: ")

    print("""
1. Round Robin
2. Least Connections
3. Random
4. Genetic Algorithm
5. IRB (Resource-based)
6. RRB (Reinforcement)
7. IoT-based CI/CD LB
8. Transfer Learning CI/CD LB
""")
    c = _read_int("Choice: ")

    if c == 1:
        res = round_robin_load(r, n)
    elif c == 2:
        res = least_connections_load(r, [0]*n)
    elif c == 3:
        res = random_load(r, n)
    elif c == 4:
        res = genetic_algorithm_load(r, n)
    elif c == 5:
        res = irb_load(r, _collect_service_caps(n))
    elif c == 6:
        res = rrb_load(r, n)
    elif c == 7:
        res = iot_lb_load(r, _collect_iot_signals(n))
    elif c == 8:
        q = list(map(float, input("Pretrained Q-values (comma): ").split(",")))
        res = tl_lb_load(r, n, q)
    else:
        return

    print(f"\n{res['algorithm']} | AvgLoad={res['average_load']:.2f}")
    save_results({
        "phase": "LoadBalancing",
        "algorithm": res["algorithm"],
        "avg_load": res["average_load"],
        "max_load": res["max_load"],
        "min_load": res["min_load"],
        "variance": res["variance"],
        "fairness_index": res["fairness_index"],
        "load_imbalance": res["load_imbalance"],
    })

# =================================================
# SCHEDULING PHASE
# =================================================

def scheduling_phase():
    print("\n--- Scheduling ---\n")
    n = _read_int("Jobs: ")
    arrival = [random.randint(0,50) for _ in range(n)]
    burst = [random.randint(1,20) for _ in range(n)]

    print("1.FCFS 2.SJF 3.SRTF 4.HRRN")
    c = _read_int("Choice: ")

    algos = {
        1: ("FCFS", fcfs_scheduling),
        2: ("SJF", sjf_scheduling),
        3: ("SRTF", srtf_scheduling),
        4: ("HRRN", hrrn_scheduling),
    }
    if c not in algos:
        return

    name, fn = algos[c]
    res = fn(arrival, burst)

    print(f"{name} | Avg WT={res['avg_waiting']:.2f}")
    save_results({
        "phase": "Scheduling",
        "algorithm": name,
        "avg_waiting": res["avg_waiting"],
        "avg_turnaround": res["avg_turnaround"],
        "avg_response": res["avg_response"],
    })

# =================================================
# MAIN
# =================================================

def main():
    while True:
        print("\n1.Build 2.LoadBalancing 3.Scheduling 4.Exit")
        c = input("Choice: ")
        if c == "1": build_phase()
        elif c == "2": load_balancing_phase()
        elif c == "3": scheduling_phase()
        elif c == "4": break

if __name__ == "__main__":
    main()
