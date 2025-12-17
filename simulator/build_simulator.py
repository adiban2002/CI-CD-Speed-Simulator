import csv
import os
import random
from typing import List, Dict

from simulator.strategy import (
    sequential_build,
    parallel_build,
    cached_build,
    slim_image_build,

    round_robin_load,
    least_connections_load,
    random_load,
    genetic_algorithm_load,
    irb_load,
    rrb_load,
    iot_based_load,
    transfer_learning_load,

    fcfs_scheduling,
    sjf_scheduling,
    srtf_scheduling,
    hrrn_scheduling
)

# -------------------------------------------------
# CSV LOGGING
# -------------------------------------------------

os.makedirs("logs", exist_ok=True)
LOG_FILE = os.path.join("logs", "results.csv")

CSV_HEADERS = [
    "phase", "strategy", "algorithm",
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response"
]


def save_results(data: Dict):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({k: data.get(k, "") for k in CSV_HEADERS})


# -------------------------------------------------
# INPUT HELPERS
# -------------------------------------------------

def _read_int(prompt: str, default: int = None) -> int:
    while True:
        try:
            s = input(prompt)
            if s == "" and default is not None:
                return default
            return int(s)
        except ValueError:
            print("Please enter a valid integer.")


def _read_float(prompt: str, default: float = None) -> float:
    while True:
        try:
            s = input(prompt)
            if s == "" and default is not None:
                return default
            return float(s)
        except ValueError:
            print("Please enter a valid number.")


# -------------------------------------------------
# BUILD PHASE
# -------------------------------------------------

def build_phase():
    print("\n--- CI/CD Build Simulator ---\n")
    num_services = _read_int("Enter number of services: ")
    avg_time = _read_int("Enter avg build time per service (minutes): ")

    print("\nChoose build strategy:")
    print("  1. Sequential Build")
    print("  2. Parallel Build")
    print("  3. Cached Build")
    print("  4. Slim Image Build")

    choice = _read_int("Your choice: ")

    if choice == 1:
        result = sequential_build(num_services, avg_time)
    elif choice == 2:
        result = parallel_build(num_services, avg_time)
    elif choice == 3:
        changed = _read_int("Enter number of changed services: ", default=0)
        result = cached_build(num_services, avg_time, changed)
    elif choice == 4:
        factor = _read_float("Enter slimming factor (default 0.7): ", default=0.7)
        result = slim_image_build(num_services, avg_time, factor)
    else:
        print("Invalid choice!")
        return

    print(f"\nStrategy: {result['strategy']}")
    print(f"Total Time: {result['total_time']} min")
    print(f"Speedup: {result['speedup']:.2f}")
    print(f"Efficiency: {result['efficiency']:.2f}")

    save_results({
        "phase": "Build",
        "strategy": result["strategy"],
        "total_time": result["total_time"],
        "speedup": result["speedup"],
        "efficiency": result["efficiency"]
    })


# -------------------------------------------------
# LOAD BALANCING PHASE
# -------------------------------------------------

def _collect_service_caps(n: int) -> List[Dict[str, float]]:
    caps = []
    for i in range(n):
        print(f"\nInstance {i}:")
        caps.append({
            "cpu_capacity": _read_float("  CPU capacity (default 10): ", 10),
            "mem_capacity": _read_float("  Memory capacity (default 8): ", 8),
            "cpu_cost": _read_float("  CPU cost per request (default 1): ", 1),
            "mem_cost": _read_float("  Memory cost per request (default 1): ", 1),
        })
    return caps


def _collect_iot_signals(n: int) -> List[Dict[str, float]]:
    print("\nEnter IoT signals for each service instance:")
    signals = []
    for i in range(n):
        print(f"\nInstance {i}:")
        signals.append({
            "latency": _read_float("  Latency (ms): "),
            "network_delay": _read_float("  Network delay (ms): "),
            "cpu_temp": _read_float("  CPU temperature (°C): ")
        })
    return signals


def load_balancing_phase():
    print("\n--- Load Balancing Simulator ---\n")
    num_services = _read_int("Enter number of service instances: ")
    requests = _read_int("Enter total incoming requests: ")

    print("\nChoose Load Balancing strategy:")
    print("  1. Round Robin")
    print("  2. Least Connections")
    print("  3. Random")
    print("  4. Genetic Algorithm")
    print("  5. IRB LB (Resource-based)")
    print("  6. RRB LB (Reinforcement)")
    print("  7. IoT-based CI/CD LB")
    print("  8. Transfer Learning CI/CD LB")

    choice = _read_int("Your choice: ")

    if choice == 1:
        result = round_robin_load(requests, num_services)

    elif choice == 2:
        initial = [0] * num_services
        result = least_connections_load(requests, initial)

    elif choice == 3:
        result = random_load(requests, num_services)

    elif choice == 4:
        result = genetic_algorithm_load(requests, num_services)

    elif choice == 5:
        caps = _collect_service_caps(num_services)
        result = irb_load(requests, caps)

    elif choice == 6:
        eps = _read_float("Epsilon (default 0.1): ", 0.1)
        lr = _read_float("Learning rate (default 0.2): ", 0.2)
        result = rrb_load(requests, num_services, epsilon=eps, lr=lr)

    elif choice == 7:
        signals = _collect_iot_signals(num_services)
        result = iot_based_load(requests, signals)

    elif choice == 8:
        print("\nEnter pretrained Q-values (comma separated)")
        q_str = input("Example: 1.2,0.8,1.5 : ")
        pretrained_q = [float(x) for x in q_str.split(",")]
        lr = _read_float("Learning rate (default 0.1): ", 0.1)
        result = transfer_learning_load(requests, num_services, pretrained_q, lr)

    else:
        print("Invalid choice!")
        return

    print(f"\nAlgorithm: {result['algorithm']}")
    print(f"Average Load: {result['average_load']:.2f}")
    print(f"Variance: {result['variance']:.2f}")
    print(f"Fairness Index: {result['fairness_index']:.4f}")
    print(f"Load Imbalance: {result['load_imbalance']:.2f}")

    save_results({
        "phase": "LoadBalancing",
        "algorithm": result["algorithm"],
        "avg_load": result["average_load"],
        "max_load": result["max_load"],
        "min_load": result["min_load"],
        "variance": result["variance"],
        "fairness_index": result["fairness_index"],
        "load_imbalance": result["load_imbalance"]
    })


# -------------------------------------------------
# SCHEDULING PHASE
# -------------------------------------------------

def scheduling_phase():
    print("\n--- CI/CD Scheduling Simulator ---\n")
    n = _read_int("Enter number of jobs: ")
    arrival = [random.randint(0, 50) for _ in range(n)]
    burst = [random.randint(1, 20) for _ in range(n)]

    print("\nChoose Scheduling Algorithm:")
    print("  1. FCFS")
    print("  2. SJF")
    print("  3. SRTF")
    print("  4. HRRN")

    choice = _read_int("Your choice: ")

    if choice == 1:
        result = fcfs_scheduling(arrival, burst)
        algo = "FCFS"
    elif choice == 2:
        result = sjf_scheduling(arrival, burst)
        algo = "SJF"
    elif choice == 3:
        result = srtf_scheduling(arrival, burst)
        algo = "SRTF"
    elif choice == 4:
        result = hrrn_scheduling(arrival, burst)
        algo = "HRRN"
    else:
        print("Invalid choice!")
        return

    print(f"\nAverage Waiting Time: {result['avg_waiting']:.2f}")
    print(f"Average Turnaround Time: {result['avg_turnaround']:.2f}")
    print(f"Average Response Time: {result['avg_response']:.2f}")

    save_results({
        "phase": "Scheduling",
        "algorithm": algo,
        "avg_waiting": result["avg_waiting"],
        "avg_turnaround": result["avg_turnaround"],
        "avg_response": result["avg_response"]
    })


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

def main():
    while True:
        print("\n--- CI/CD Simulator Menu ---")
        print("  1. Build Phase")
        print("  2. Load Balancing Phase")
        print("  3. Scheduling Phase")
        print("  4. Exit")

        choice = input("Select phase: ")

        if choice == "1":
            build_phase()
        elif choice == "2":
            load_balancing_phase()
        elif choice == "3":
            scheduling_phase()
        elif choice == "4":
            print("Exiting simulator.")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
