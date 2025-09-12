import csv
import os
import random
from simulator.strategy import (
    sequential_build,
    parallel_build,
    cached_build,
    slim_image_build,
    round_robin_load,
    least_connections_load,
    random_load,
    genetic_algorithm_load,
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

def save_results(data):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        if not file_exists:
            writer.writeheader()
        row = {key: data.get(key, "") for key in CSV_HEADERS}
        writer.writerow(row)


def build_phase():
    print("\n--- CI/CD Build Simulator ---\n")
    num_services = int(input("Enter number of services: "))
    avg_time = int(input("Enter avg build time per service (minutes): "))

    print("\nChoose build strategy:")
    print("  1. Sequential Build")
    print("  2. Parallel Build")
    print("  3. Cached Build")
    print("  4. Slim Image Build")
    choice = int(input("Your choice: "))

    if choice == 1:
        result = sequential_build(num_services, avg_time)
    elif choice == 2:
        result = parallel_build(num_services, avg_time)
    elif choice == 3:
        changed = int(input("Enter number of changed services: "))
        result = cached_build(num_services, avg_time, changed)
    elif choice == 4:
        factor = float(input("Enter slimming factor (default 0.7): ") or 0.7)
        result = slim_image_build(num_services, avg_time, factor)
    else:
        print("Invalid choice!")
        return

    print(f"\nStrategy: {result['strategy']}")
    print(f"Estimated Build Time: {result['total_time']} minutes")
    print(f"Speedup: {result['speedup']:.2f}")
    print(f"Efficiency: {result['efficiency']:.2f}")

    save_results({
        "phase": "Build",
        "strategy": result["strategy"],
        "total_time": result["total_time"],
        "speedup": f"{result['speedup']:.2f}",
        "efficiency": f"{result['efficiency']:.2f}"
    })


def load_balancing_phase():
    print("\n--- Load Balancing Simulator ---\n")
    num_services = int(input("Enter number of service instances: "))
    requests = int(input("Enter total incoming requests: "))

    print("\nChoose Load Balancing strategy:")
    print("  1. Round Robin")
    print("  2. Least Connections")
    print("  3. Random")
    print("  4. Genetic Algorithm")
    choice = int(input("Your choice: "))

    if choice == 1:
        result = round_robin_load(requests, num_services)
    elif choice == 2:
        initial_loads = [0] * num_services
        result = least_connections_load(requests, initial_loads)
    elif choice == 3:
        result = random_load(requests, num_services)
    elif choice == 4:
        result = genetic_algorithm_load(requests, num_services)
    else:
        print("Invalid choice!")
        return

    print(f"\nAlgorithm: {result['algorithm']}")

    non_zero = [(i, load) for i, load in enumerate(result["distribution"]) if load > 0]
    if not non_zero:
        print("No requests were distributed.")
    elif len(non_zero) > 20:
        preview = non_zero[:20]
        print(f"Request distribution (first 20 non-zero services): {preview} ...")
    else:
        print(f"Request distribution (non-zero services): {non_zero}")

    print(f"Average Load: {result['average_load']:.2f}")
    print(f"Max Load: {result['max_load']}")
    print(f"Min Load: {result['min_load']}")
    print(f"Variance: {result['variance']:.2f}")
    print(f"Fairness Index: {result['fairness_index']:.4f}")
    print(f"Load Imbalance: {result['load_imbalance']:.2f}")

    save_results({
        "phase": "LoadBalancing",
        "algorithm": result["algorithm"],
        "avg_load": f"{result['average_load']:.2f}",
        "max_load": result["max_load"],
        "min_load": result["min_load"],
        "variance": f"{result['variance']:.2f}",
        "fairness_index": f"{result['fairness_index']:.4f}",
        "load_imbalance": f"{result['load_imbalance']:.2f}"
    })


def scheduling_phase():
    print("\n--- CI/CD Scheduling Simulator ---\n")
    n = int(input("Enter number of jobs (processes): "))
    arrival_times = []
    burst_times = []

    if n <= 200:
        for i in range(n):
            at = int(input(f"Arrival time of job {i+1}: "))
            bt = int(input(f"Burst time of job {i+1}: "))
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
    choice = int(input("Your choice: "))

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

    print(f"\nAverage Waiting Time: {result['avg_waiting']:.2f}")
    print(f"Average Turnaround Time: {result['avg_turnaround']:.2f}")
    print(f"Average Response Time: {result['avg_response']:.2f}")

    save_results({
        "phase": "Scheduling",
        "algorithm": ["FCFS", "SJF", "SRTF", "HRRN"][choice-1],
        "avg_waiting": f"{result['avg_waiting']:.2f}",
        "avg_turnaround": f"{result['avg_turnaround']:.2f}",
        "avg_response": f"{result['avg_response']:.2f}"
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
