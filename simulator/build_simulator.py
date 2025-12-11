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
    fcfs_scheduling,
    sjf_scheduling,
    srtf_scheduling,
    hrrn_scheduling
)

# Create logs folder if not exists
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
        row = {key: data.get(key, "") for key in CSV_HEADERS}
        writer.writerow(row)


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

    print(f"\nStrategy: {result.get('strategy', '')}")
    print(f"Estimated Build Time: {result.get('total_time', '')} minutes")
    print(f"Speedup: {float(result.get('speedup', 0)):.2f}")
    print(f"Efficiency: {float(result.get('efficiency', 0)):.2f}")

    save_results({
        "phase": "Build",
        "strategy": result.get("strategy", ""),
        "total_time": result.get("total_time", ""),
        "speedup": f"{result.get('speedup', '')}",
        "efficiency": f"{result.get('efficiency', '')}"
    })


def _collect_service_caps(num_services: int) -> List[Dict[str, float]]:
    print("\nEnter instance capacities for each service instance.")
    caps = []
    for i in range(num_services):
        print(f"\nInstance #{i}:")
        cpu_cap = _read_float("  CPU capacity (units, default 10): ", default=10.0)
        mem_cap = _read_float("  Memory capacity (units, default 8): ", default=8.0)
        cpu_cost = _read_float("  CPU cost per request (default 1): ", default=1.0)
        mem_cost = _read_float("  Memory cost per request (default 1): ", default=1.0)
        caps.append({
            "cpu_capacity": cpu_cap,
            "mem_capacity": mem_cap,
            "cpu_cost": cpu_cost,
            "mem_cost": mem_cost
        })
    return caps


def load_balancing_phase():
    print("\n--- Load Balancing Simulator ---\n")
    num_services = _read_int("Enter number of service instances: ")
    requests = _read_int("Enter total incoming requests: ")

    print("\nChoose Load Balancing strategy:")
    print("  1. Round Robin")
    print("  2. Least Connections")
    print("  3. Random")
    print("  4. Genetic Algorithm")
    print("  5. IRB LB (Instance Resource-Based)")
    print("  6. RRB LB (Reinforcement Round-Robin)")
    choice = _read_int("Your choice: ")

    result = None

    if choice == 1:
        result = round_robin_load(requests, num_services)
    elif choice == 2:
        print("Do you want to provide initial loads? (press Enter to use zeros)")
        s = input("Enter comma-separated initial loads (e.g. 2,0,1,4): ").strip()
        if s:
            try:
                initial_loads = [int(x.strip()) for x in s.split(",")]
                if len(initial_loads) != num_services:
                    print("Length mismatch: falling back to zeros.")
                    initial_loads = [0] * num_services
            except ValueError:
                print("Invalid format: falling back to zeros.")
                initial_loads = [0] * num_services
        else:
            initial_loads = [0] * num_services
        result = least_connections_load(requests, initial_loads)
    elif choice == 3:
        result = random_load(requests, num_services)
    elif choice == 4:
        gens = _read_int("Generations (default 50): ", default=50)
        pop = _read_int("Population size (default 10): ", default=10)
        result = genetic_algorithm_load(requests, num_services, generations=gens, population_size=pop)
    elif choice == 5:
        caps = _collect_service_caps(num_services)
        result = irb_load(requests, caps)
    elif choice == 6:
        epsilon = _read_float("Epsilon (exploration probability, default 0.1): ", default=0.1)
        lr = _read_float("Learning rate (default 0.2): ", default=0.2)
        base_low = _read_float("Base response time low (default 1.0): ", default=1.0)
        base_high = _read_float("Base response time high (default 3.0): ", default=3.0)
        result = rrb_load(requests, num_services, epsilon=epsilon, learning_rate=lr,
                          base_resp_low=base_low, base_resp_high=base_high)
    else:
        print("Invalid choice!")
        return

    print(f"\nAlgorithm: {result.get('algorithm', 'Unknown')}")

    distribution = result.get("distribution", [])
    non_zero = [(i, load) for i, load in enumerate(distribution) if load > 0]
    if not non_zero:
        print("No requests were distributed.")
    elif len(non_zero) > 20:
        preview = non_zero[:20]
        print(f"Request distribution (first 20 non-zero services): {preview} ...")
    else:
        print(f"Request distribution (non-zero services): {non_zero}")

    print(f"Average Load: {result.get('average_load', 0):.2f}")
    print(f"Max Load: {result.get('max_load', 0)}")
    print(f"Min Load: {result.get('min_load', 0)}")
    print(f"Variance: {result.get('variance', 0):.2f}")
    print(f"Fairness Index: {result.get('fairness_index', 0):.4f}")
    print(f"Load Imbalance: {result.get('load_imbalance', 0):.2f}")

    if choice == 5:
        cap_summary = result.get("service_capacities_summary", [])
        print("\nInstance capacities summary:")
        for i, c in enumerate(cap_summary):
            print(f"  Instance {i}: CPU={c.get('cpu_capacity')} MEM={c.get('mem_capacity')}")
    if choice == 6:
        print("\nRRB final Q-values:", result.get("Q_values", []))
        print("RRB base response characteristics:", result.get("base_response_characteristics", []))

    save_results({
        "phase": "LoadBalancing",
        "algorithm": result.get("algorithm", ""),
        "avg_load": f"{result.get('average_load', ''):.2f}" if "average_load" in result else "",
        "max_load": result.get("max_load", ""),
        "min_load": result.get("min_load", ""),
        "variance": f"{result.get('variance', ''):.2f}" if "variance" in result else "",
        "fairness_index": f"{result.get('fairness_index', ''):.4f}" if "fairness_index" in result else "",
        "load_imbalance": f"{result.get('load_imbalance', ''):.2f}" if "load_imbalance" in result else ""
    })


def scheduling_phase():
    print("\n--- CI/CD Scheduling Simulator ---\n")
    n = _read_int("Enter number of jobs (processes): ")
    arrival_times = []
    burst_times = []

    if n <= 200:
        for i in range(n):
            at = _read_int(f"Arrival time of job {i+1}: ")
            bt = _read_int(f"Burst time of job {i+1}: ")
            arrival_times.append(at)
            burst_times.append(bt)
    else:
        print(f"\nGenerating dataset automatically for {n} jobs...")
        arrival_times = [random.randint(0, 1000) for _ in range(n)]
        burst_times = [random.randint(1, 20) for _ in range(n)]

    print("\nChoose Scheduling Algorithm:")
    print("  1. FCFS")
    print("  2. SJF (Non-preemptive)")
    print("  3. SRTF (Preemptive SJF)")
    print("  4. HRRN (Highest Response Ratio Next)")
    choice = _read_int("Your choice: ")

    if choice == 1:
        result = fcfs_scheduling(arrival_times, burst_times)
    elif choice == 2:
        result = sjf_scheduling(arrival_times, burst_times)
    elif choice == 3:
        result = srtf_scheduling(arrival_times, burst_times)
    elif choice == 4:
        result = hrrn_scheduling(arrival_times, burst_times)
    else:
        print("Invalid choice!")
        return

    if n <= 200:
        print("\n--- Results ---")
        for i in range(n):
            print(f"Job {i+1}: AT={arrival_times[i]}, BT={burst_times[i]}, "
                  f"CT={result['completion_times'][i]}, "
                  f"TAT={result['turnaround_times'][i]}, "
                  f"WT={result['waiting_times'][i]}, "
                  f"RT={result['response_times'][i]}")

    print(f"\nAverage Waiting Time: {result.get('avg_waiting', 0):.2f}")
    print(f"Average Turnaround Time: {result.get('avg_turnaround', 0):.2f}")
    print(f"Average Response Time: {result.get('avg_response', 0):.2f}")

    save_results({
        "phase": "Scheduling",
        "algorithm": ["FCFS", "SJF", "SRTF", "HRRN"][choice-1] if 1 <= choice <= 4 else "",
        "avg_waiting": f"{result.get('avg_waiting', ''):.2f}" if "avg_waiting" in result else "",
        "avg_turnaround": f"{result.get('avg_turnaround', ''):.2f}" if "avg_turnaround" in result else "",
        "avg_response": f"{result.get('avg_response', ''):.2f}" if "avg_response" in result else ""
    })


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
            print("Exiting simulator. Goodbye!")
            break
        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()
