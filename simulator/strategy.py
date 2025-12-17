from typing import List, Dict
import random
import statistics


# =========================================================
# BUILD STRATEGIES
# =========================================================

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
    return {
        "strategy": "Cached Build",
        "total_time": total_time,
        "speedup": round(speedup, 2),
        "efficiency": round(speedup, 2),
    }


def slim_image_build(num_services: int, avg_time: int, slimming_factor: float = 0.7) -> Dict:
    seq_time = num_services * avg_time
    total_time = int(seq_time * slimming_factor)
    speedup = seq_time / total_time
    return {
        "strategy": "Slim Image Build",
        "total_time": total_time,
        "speedup": round(speedup, 2),
        "efficiency": round(speedup, 2),
    }


# =========================================================
# COMMON LOAD METRICS
# =========================================================

def compute_load_metrics(distribution: List[int]) -> Dict:
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
    avg = total / n
    variance = statistics.pvariance(distribution)
    sum_sq = sum(x ** 2 for x in distribution)
    fairness = (total ** 2) / (n * sum_sq) if sum_sq > 0 else 1.0

    return {
        "distribution": distribution,
        "average_load": avg,
        "max_load": max(distribution),
        "min_load": min(distribution),
        "variance": variance,
        "fairness_index": fairness,
        "load_imbalance": max(distribution) - min(distribution)
    }


# =========================================================
# CLASSIC LOAD BALANCERS
# =========================================================

def round_robin_load(requests: int, num_services: int) -> Dict:
    dist = [0] * num_services
    for i in range(requests):
        dist[i % num_services] += 1
    m = compute_load_metrics(dist)
    m["algorithm"] = "Round Robin"
    return m


def least_connections_load(requests: int, service_loads: List[int]) -> Dict:
    loads = service_loads[:]
    for _ in range(requests):
        idx = loads.index(min(loads))
        loads[idx] += 1
    m = compute_load_metrics(loads)
    m["algorithm"] = "Least Connections"
    return m


def random_load(requests: int, num_services: int) -> Dict:
    dist = [0] * num_services
    for _ in range(requests):
        dist[random.randint(0, num_services - 1)] += 1
    m = compute_load_metrics(dist)
    m["algorithm"] = "Random"
    return m


# =========================================================
# GENETIC ALGORITHM LOAD BALANCER
# =========================================================

def genetic_algorithm_load(requests: int, num_services: int,
                           generations: int = 40, population_size: int = 10) -> Dict:
    def fitness(d): return -statistics.pvariance(d)

    pop = []
    for _ in range(population_size):
        d = [0] * num_services
        for _ in range(requests):
            d[random.randint(0, num_services - 1)] += 1
        pop.append(d)

    for _ in range(generations):
        pop.sort(key=fitness, reverse=True)
        new_pop = pop[:2]
        while len(new_pop) < population_size:
            p1, p2 = random.sample(pop[:5], 2)
            cut = random.randint(1, num_services - 1)
            child = p1[:cut] + p2[cut:]
            diff = requests - sum(child)
            for _ in range(abs(diff)):
                i = random.randint(0, num_services - 1)
                child[i] += 1 if diff > 0 else -1 if child[i] > 0 else 0
            new_pop.append(child)
        pop = new_pop

    m = compute_load_metrics(pop[0])
    m["algorithm"] = "Genetic Algorithm LB"
    return m


# =========================================================
# IRB LOAD BALANCER
# =========================================================

def irb_load(requests: int, service_caps: List[Dict[str, float]]) -> Dict:
    n = len(service_caps)
    used_cpu = [0.0] * n
    used_mem = [0.0] * n
    dist = [0] * n

    for _ in range(requests):
        scores = []
        for i in range(n):
            cpu = service_caps[i]["cpu_capacity"] - used_cpu[i]
            mem = service_caps[i]["mem_capacity"] - used_mem[i]
            scores.append(cpu + mem)
        idx = scores.index(max(scores))
        dist[idx] += 1
        used_cpu[idx] += service_caps[idx].get("cpu_cost", 1.0)
        used_mem[idx] += service_caps[idx].get("mem_cost", 1.0)

    m = compute_load_metrics(dist)
    m["algorithm"] = "IRB LB"
    return m


# =========================================================
# RRB LOAD BALANCER
# =========================================================

def rrb_load(requests: int, num_services: int,
             epsilon: float = 0.1, lr: float = 0.2) -> Dict:
    Q = [1.0] * num_services
    dist = [0] * num_services
    loads = [0] * num_services

    for _ in range(requests):
        idx = random.randint(0, num_services - 1) if random.random() < epsilon else Q.index(max(Q))
        response = 1 + 0.15 * loads[idx]
        reward = 1 / response
        Q[idx] += lr * (reward - Q[idx])
        dist[idx] += 1
        loads[idx] += 1

    m = compute_load_metrics(dist)
    m["algorithm"] = "RRB LB"
    return m


# =========================================================
# 🔥 NEW: IoT-AWARE CI/CD LOAD BALANCER
# =========================================================

def iot_based_load(requests: int, iot_signals: List[Dict[str, float]]) -> Dict:
    """
    Uses IoT signals (latency, cpu_temp, network_delay) to route CI/CD jobs.
    """
    n = len(iot_signals)
    dist = [0] * n

    for _ in range(requests):
        scores = []
        for s in iot_signals:
            score = (
                (1 / (s["latency"] + 1e-6)) +
                (1 / (s["network_delay"] + 1e-6)) +
                (1 / (s["cpu_temp"] + 1e-6))
            )
            scores.append(score)
        idx = scores.index(max(scores))
        dist[idx] += 1

    m = compute_load_metrics(dist)
    m["algorithm"] = "IoT-based CI/CD LB"
    return m


# =========================================================
# 🔥 NEW: TRANSFER LEARNING CI/CD LOAD BALANCER
# =========================================================

def transfer_learning_load(requests: int,
                           num_services: int,
                           pretrained_Q: List[float],
                           lr: float = 0.1) -> Dict:
    """
    Initializes LB policy from pretrained knowledge (transfer learning).
    """
    Q = pretrained_Q[:num_services]
    dist = [0] * num_services
    loads = [0] * num_services

    for _ in range(requests):
        idx = Q.index(max(Q))
        response = 1 + 0.2 * loads[idx]
        reward = 1 / response
        Q[idx] += lr * (reward - Q[idx])
        dist[idx] += 1
        loads[idx] += 1

    m = compute_load_metrics(dist)
    m["algorithm"] = "TL-based CI/CD LB"
    m["final_Q"] = [round(q, 3) for q in Q]
    return m
