from typing import List, Dict
import random
import statistics

def sequential_build(num_services: int, avg_time: int) -> Dict:
    total_time = num_services * avg_time
    return {
        "strategy": "Sequential Build",
        "total_time": total_time,
        "speedup": 1.0,
        "efficiency": 1.0
    }


def parallel_build(num_services: int, avg_time: int) -> Dict:
    total_time = avg_time
    seq_time = num_services * avg_time
    speedup = seq_time / total_time
    efficiency = speedup / num_services
    return {
        "strategy": "Parallel Build",
        "total_time": total_time,
        "speedup": round(speedup, 2),
        "efficiency": round(efficiency, 2),
    }


def cached_build(num_services: int, avg_time: int, changed_services: int) -> Dict:
    seq_time = num_services * avg_time
    cached_time = (num_services - changed_services) * (avg_time // 2)
    total_time = changed_services * avg_time + cached_time
    speedup = seq_time / total_time
    efficiency = speedup
    return {
        "strategy": "Cached Build",
        "total_time": total_time,
        "speedup": round(speedup, 2),
        "efficiency": round(efficiency, 2),
    }


def slim_image_build(num_services: int, avg_time: int, slimming_factor: float = 0.7) -> Dict:
    seq_time = num_services * avg_time
    total_time = int(seq_time * slimming_factor)
    speedup = seq_time / total_time
    efficiency = speedup
    return {
        "strategy": "Slim Image Build",
        "total_time": total_time,
        "speedup": round(speedup, 2),
        "efficiency": round(efficiency, 2),
    }


def compute_load_metrics(distribution: List[int]) -> Dict:
    """
    Compute common load metrics used by all load-balancing algorithms.
    """
    n = len(distribution)
    if n == 0:
        return {
            "distribution": distribution,
            "average_load": 0,
            "max_load": 0,
            "min_load": 0,
            "variance": 0,
            "fairness_index": 1.0,
            "load_imbalance": 0
        }

    total = sum(distribution)
    avg_load = total / n
    max_load_value = max(distribution)
    min_load_value = min(distribution)
    variance = statistics.pvariance(distribution) if n > 0 else 0
    sum_sq = sum(x ** 2 for x in distribution)
    fairness = (total ** 2 / (n * sum_sq)) if total > 0 and sum_sq > 0 else 1.0
    load_imbalance = max_load_value - min_load_value
    return {
        "distribution": distribution,
        "average_load": avg_load,
        "max_load": max_load_value,
        "min_load": min_load_value,
        "variance": variance,
        "fairness_index": fairness,
        "load_imbalance": load_imbalance
    }


def round_robin_load(requests: int, num_services: int) -> Dict:
    distribution = [0] * num_services
    for i in range(requests):
        distribution[i % num_services] += 1
    metrics = compute_load_metrics(distribution)
    metrics["algorithm"] = "Round Robin"
    return metrics


def least_connections_load(requests: int, service_loads: List[int]) -> Dict:
    loads = service_loads[:]
    for _ in range(requests):
        idx = loads.index(min(loads))
        loads[idx] += 1
    metrics = compute_load_metrics(loads)
    metrics["algorithm"] = "Least Connections"
    return metrics


def random_load(requests: int, num_services: int) -> Dict:
    distribution = [0] * num_services
    for _ in range(requests):
        distribution[random.randint(0, num_services - 1)] += 1
    metrics = compute_load_metrics(distribution)
    metrics["algorithm"] = "Random"
    return metrics


def genetic_algorithm_load(requests: int, num_services: int,
                           generations: int = 50, population_size: int = 10) -> Dict:
    def fitness(distribution: List[int]) -> float:
        # maximize negative variance -> more balanced = higher fitness (less variance)
        return -statistics.pvariance(distribution) if len(distribution) > 0 else 0.0

    population = []
    for _ in range(population_size):
        dist = [0] * num_services
        for _ in range(requests):
            dist[random.randint(0, num_services - 1)] += 1
        population.append(dist)

    for _ in range(generations):
        population = sorted(population, key=fitness, reverse=True)
        new_population = population[:2]  # elitism: keep top 2

        while len(new_population) < population_size:
            # choose parents from the top half (or fewer if small pop)
            top_k = max(2, min(len(population), population_size // 2))
            p1, p2 = random.sample(population[:top_k], 2)
            cut = random.randint(1, num_services - 1) if num_services > 1 else 0
            child = p1[:cut] + p2[cut:]
            diff = requests - sum(child)
            for _ in range(abs(diff)):
                idx = random.randint(0, num_services - 1)
                if diff > 0:
                    child[idx] += 1
                elif diff < 0 and child[idx] > 0:
                    child[idx] -= 1
            new_population.append(child)

        # mutation
        for i in range(2, population_size):
            if random.random() < 0.2 and num_services > 1:
                a, b = random.sample(range(num_services), 2)
                if new_population[i][a] > 0:
                    new_population[i][a] -= 1
                    new_population[i][b] += 1

        population = new_population

    best = population[0]
    metrics = compute_load_metrics(best)
    metrics["algorithm"] = "Genetic Algorithm (Load Balancing)"
    return metrics


def compute_detailed_metrics(arrival_times: List[int], burst_times: List[int], order: List[int]) -> Dict:
    n = len(burst_times)
    if n == 0:
        return {
            "arrival_times": arrival_times,
            "burst_times": burst_times,
            "order": order,
            "start_times": [],
            "completion_times": [],
            "waiting_times": [],
            "turnaround_times": [],
            "response_times": [],
            "avg_waiting": 0,
            "avg_turnaround": 0,
            "avg_response": 0,
        }

    completion_times = [0] * n
    turnaround_times = [0] * n
    waiting_times = [0] * n
    response_times = [0] * n
    start_times = [0] * n

    time = 0
    for idx in order:
        if time < arrival_times[idx]:
            time = arrival_times[idx]
        start_times[idx] = time
        completion_times[idx] = time + burst_times[idx]
        turnaround_times[idx] = completion_times[idx] - arrival_times[idx]
        waiting_times[idx] = turnaround_times[idx] - burst_times[idx]
        response_times[idx] = start_times[idx] - arrival_times[idx]
        time = completion_times[idx]

    return {
        "arrival_times": arrival_times,
        "burst_times": burst_times,
        "order": order,
        "start_times": start_times,
        "completion_times": completion_times,
        "waiting_times": waiting_times,
        "turnaround_times": turnaround_times,
        "response_times": response_times,
        "avg_waiting": sum(waiting_times) / n if n > 0 else 0,
        "avg_turnaround": sum(turnaround_times) / n if n > 0 else 0,
        "avg_response": sum(response_times) / n if n > 0 else 0,
    }


def fcfs_scheduling(arrival_times: List[int], burst_times: List[int]) -> Dict:
    order = sorted(range(len(arrival_times)), key=lambda i: arrival_times[i])
    return compute_detailed_metrics(arrival_times, burst_times, order)


def sjf_scheduling(arrival_times: List[int], burst_times: List[int]) -> Dict:
    n = len(burst_times)
    order = []
    time = 0
    remaining = set(range(n))

    while remaining:
        available = [i for i in remaining if arrival_times[i] <= time]
        if not available:
            time = min(arrival_times[i] for i in remaining)
            available = [i for i in remaining if arrival_times[i] <= time]

        shortest = min(available, key=lambda i: burst_times[i])
        order.append(shortest)
        time += burst_times[shortest]
        remaining.remove(shortest)

    return compute_detailed_metrics(arrival_times, burst_times, order)


def srtf_scheduling(arrival_times: List[int], burst_times: List[int]) -> Dict:
    n = len(burst_times)
    remaining_times = burst_times[:]
    completion_times = [0] * n
    start_times = [-1] * n
    response_times = [0] * n

    time = 0
    completed = 0
    order = []

    while completed < n:
        available = [i for i in range(n) if arrival_times[i] <= time and remaining_times[i] > 0]

        if not available:
            time += 1
            continue

        shortest = min(available, key=lambda i: remaining_times[i])

        if start_times[shortest] == -1:
            start_times[shortest] = time
            response_times[shortest] = time - arrival_times[shortest]

        order.append(shortest)
        remaining_times[shortest] -= 1
        time += 1

        if remaining_times[shortest] == 0:
            completion_times[shortest] = time
            completed += 1

    turnaround_times = [completion_times[i] - arrival_times[i] for i in range(n)]
    waiting_times = [turnaround_times[i] - burst_times[i] for i in range(n)]

    return {
        "arrival_times": arrival_times,
        "burst_times": burst_times,
        "order": order,
        "start_times": start_times,
        "completion_times": completion_times,
        "waiting_times": waiting_times,
        "turnaround_times": turnaround_times,
        "response_times": response_times,
        "avg_waiting": sum(waiting_times) / n if n > 0 else 0,
        "avg_turnaround": sum(turnaround_times) / n if n > 0 else 0,
        "avg_response": sum(response_times) / n if n > 0 else 0,
    }


def hrrn_scheduling(arrival_times: List[int], burst_times: List[int]) -> Dict:
    n = len(burst_times)
    time = 0
    completed = 0
    order = []
    completion_times = [0] * n
    waiting_times = [0] * n
    turnaround_times = [0] * n
    response_times = [0] * n
    start_times = [-1] * n
    done = [False] * n

    while completed < n:
        available = [i for i in range(n) if not done[i] and arrival_times[i] <= time]
        if not available:
            time += 1
            continue

        ratios = {i: (time - arrival_times[i] + burst_times[i]) / burst_times[i] for i in available}
        chosen = max(ratios, key=ratios.get)

        if start_times[chosen] == -1:
            start_times[chosen] = time
            response_times[chosen] = time - arrival_times[chosen]

        order.append(chosen)
        time += burst_times[chosen]
        completion_times[chosen] = time
        turnaround_times[chosen] = completion_times[chosen] - arrival_times[chosen]
        waiting_times[chosen] = turnaround_times[chosen] - burst_times[chosen]
        done[chosen] = True
        completed += 1

    return {
        "arrival_times": arrival_times,
        "burst_times": burst_times,
        "order": order,
        "start_times": start_times,
        "completion_times": completion_times,
        "waiting_times": waiting_times,
        "turnaround_times": turnaround_times,
        "response_times": response_times,
        "avg_waiting": sum(waiting_times) / n if n > 0 else 0,
        "avg_turnaround": sum(turnaround_times) / n if n > 0 else 0,
        "avg_response": sum(response_times) / n if n > 0 else 0,
    }


# --- Intelligent CI/CD Load Balancing Algorithms (IRB LB & RRB LB) ---

def irb_load(requests: int, service_caps: List[Dict[str, float]]) -> Dict:
    """
    IRB LB: Instance Resource-Based Load Balancer (simulated).
    service_caps: list of dicts, each with keys:
      - 'cpu_capacity' (float) : max CPU units available
      - 'mem_capacity' (float) : max memory units available
      - optionally 'cpu_cost' (float) : cost per request in CPU units (default 1)
      - optionally 'mem_cost' (float) : cost per request in memory units (default 1)
    Strategy:
      For each incoming request, pick the instance with the largest available capacity
      where available capacity is computed as (cpu_capacity - used_cpu) + (mem_capacity - used_mem).
    Returns compute_load_metrics on final distribution with algorithm name and a summary of capacities.
    """
    num_services = len(service_caps)
    if num_services == 0:
        return compute_load_metrics([])  # empty

    used_cpu = [0.0] * num_services
    used_mem = [0.0] * num_services
    distribution = [0] * num_services

    # normalize missing fields and ensure floats
    caps = []
    for s in service_caps:
        caps.append({
            "cpu_capacity": float(s.get("cpu_capacity", 1.0)),
            "mem_capacity": float(s.get("mem_capacity", 1.0)),
            "cpu_cost": float(s.get("cpu_cost", 1.0)),
            "mem_cost": float(s.get("mem_cost", 1.0)),
        })

    for _ in range(requests):
        # compute available capacity for every service
        avail = []
        for i in range(num_services):
            cpu_avail = max(0.0, caps[i]["cpu_capacity"] - used_cpu[i])
            mem_avail = max(0.0, caps[i]["mem_capacity"] - used_mem[i])
            # weighted sum: CPU and MEM both matter (weights = 1 here, could be tuned)
            avail_score = cpu_avail + mem_avail
            avail.append(avail_score)

        # pick service with maximum available capacity (break ties by lower index)
        idx = max(range(num_services), key=lambda i: (avail[i], -i))
        distribution[idx] += 1
        used_cpu[idx] += caps[idx]["cpu_cost"]
        used_mem[idx] += caps[idx]["mem_cost"]

    metrics = compute_load_metrics(distribution)
    metrics["algorithm"] = "IRB LB (Instance Resource-Based)"
    metrics["service_capacities_summary"] = [
        {"cpu_capacity": c["cpu_capacity"], "mem_capacity": c["mem_capacity"]} for c in caps
    ]
    return metrics


def rrb_load(requests: int, num_services: int, epsilon: float = 0.1,
             learning_rate: float = 0.2, base_resp_low: float = 1.0,
             base_resp_high: float = 3.0) -> Dict:
    """
    RRB LB: Reinforcement Round-Robin / Reward-based load balancer (simulated).
    - Uses epsilon-greedy selection over Q-values per service.
    - Simulates a response time for each assignment which depends on current load.
    - Q-values are updated online with a simple TD-like rule: Q <- Q + lr * (reward - Q)
      where reward = 1 / response_time (higher reward for lower response time).
    - Parameters:
      epsilon: exploration probability
      learning_rate: how quickly Q-values are updated
      base_resp_low/high: base response time range for services (randomized per service)
    Returns metrics computed with compute_load_metrics and final Q-values.
    """
    if num_services <= 0:
        return compute_load_metrics([])

    Q = [1.0] * num_services  # estimated value (higher is better)
    distribution = [0] * num_services
    loads = [0] * num_services
    # assign each service a base response characteristic
    base_resp = [random.uniform(base_resp_low, base_resp_high) for _ in range(num_services)]

    for _ in range(requests):
        # epsilon-greedy selection
        if random.random() < epsilon:
            idx = random.randint(0, num_services - 1)
        else:
            idx = max(range(num_services), key=lambda i: Q[i])

        # simulate response time: base_resp * (1 + alpha * load)
        alpha = 0.15  # tunable sensitivity to load
        response_time = base_resp[idx] * (1.0 + alpha * loads[idx])

        # compute reward and update Q
        reward = 1.0 / (response_time + 1e-9)  # avoid div0
        Q[idx] = Q[idx] + learning_rate * (reward - Q[idx])

        # assign request
        distribution[idx] += 1
        loads[idx] += 1

    metrics = compute_load_metrics(distribution)
    metrics["algorithm"] = "RRB LB (Reinforcement Round-Robin)"
    metrics["Q_values"] = [round(q, 4) for q in Q]
    metrics["base_response_characteristics"] = [round(b, 3) for b in base_resp]
    return metrics
