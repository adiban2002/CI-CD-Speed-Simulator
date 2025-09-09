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
    avg_load = sum(distribution) / len(distribution)
    max_load_value = max(distribution)
    min_load_value = min(distribution)
    variance = statistics.pvariance(distribution)
    fairness = sum(distribution) ** 2 / (len(distribution) * sum(x ** 2 for x in distribution)) if sum(distribution) > 0 else 1.0
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
        return -statistics.pvariance(distribution)

    population = []
    for _ in range(population_size):
        dist = [0] * num_services
        for _ in range(requests):
            dist[random.randint(0, num_services - 1)] += 1
        population.append(dist)

    for _ in range(generations):
        population = sorted(population, key=fitness, reverse=True)
        new_population = population[:2]

        while len(new_population) < population_size:
            p1, p2 = random.sample(population[:5], 2)
            cut = random.randint(1, num_services - 1)
            child = p1[:cut] + p2[cut:]
            diff = requests - sum(child)
            for _ in range(abs(diff)):
                idx = random.randint(0, num_services - 1)
                if diff > 0:
                    child[idx] += 1
                elif diff < 0 and child[idx] > 0:
                    child[idx] -= 1
            new_population.append(child)

        for i in range(2, population_size):
            if random.random() < 0.2:
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
        "avg_waiting": sum(waiting_times) / n,
        "avg_turnaround": sum(turnaround_times) / n,
        "avg_response": sum(response_times) / n,
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
        "avg_waiting": sum(waiting_times) / n,
        "avg_turnaround": sum(turnaround_times) / n,
        "avg_response": sum(response_times) / n,
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
        "avg_waiting": sum(waiting_times) / n,
        "avg_turnaround": sum(turnaround_times) / n,
        "avg_response": sum(response_times) / n,
    }
