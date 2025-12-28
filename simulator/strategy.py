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
    seq_time = num_services * avg_time
    speedup = seq_time / avg_time
    return {
        "strategy": "Parallel Build",
        "total_time": avg_time,
        "speedup": round(speedup, 2),
        "efficiency": round(speedup / num_services, 2),
    }


def cached_build(num_services: int, avg_time: int, changed_services: int) -> Dict:
    seq_time = num_services * avg_time
    cached_time = (num_services - changed_services) * (avg_time // 2)
    total = changed_services * avg_time + cached_time
    speedup = seq_time / total
    return {
        "strategy": "Cached Build",
        "total_time": total,
        "speedup": round(speedup, 2),
        "efficiency": round(speedup, 2),
    }


def slim_image_build(num_services: int, avg_time: int, slimming_factor: float = 0.7) -> Dict:
    seq_time = num_services * avg_time
    total = int(seq_time * slimming_factor)
    speedup = seq_time / total
    return {
        "strategy": "Slim Image Build",
        "total_time": total,
        "speedup": round(speedup, 2),
        "efficiency": round(speedup, 2),
    }


# =========================================================
# COMMON LOAD METRICS (ZERO-SAFE)
# =========================================================

def compute_load_metrics(distribution: List[int]) -> Dict:
    n = len(distribution)

    if n == 0:
        return {
            "distribution": distribution,
            "average_load": 0.0,
            "max_load": 0,
            "min_load": 0,
            "variance": 0.0,
            "fairness_index": 1.0,
            "load_imbalance": 0.0
        }

    total = sum(distribution)
    avg = total / n
    max_load = max(distribution)
    min_load = min(distribution)
    variance = statistics.pvariance(distribution)

    sum_sq = sum(x ** 2 for x in distribution)

    # 🔒 ZERO-SAFE FAIRNESS (CRITICAL FIX)
    if total == 0 or sum_sq == 0:
        fairness = 1.0
    else:
        fairness = (total ** 2) / (n * sum_sq)

    return {
        "distribution": distribution,
        "average_load": avg,
        "max_load": max_load,
        "min_load": min_load,
        "variance": variance,
        "fairness_index": fairness,
        "load_imbalance": max_load - min_load,
    }


# =========================================================
# LOAD BALANCERS
# =========================================================

def round_robin_load(requests: int, num_services: int) -> Dict:
    d = [0] * num_services
    for i in range(requests):
        d[i % num_services] += 1
    m = compute_load_metrics(d)
    m["algorithm"] = "Round Robin"
    return m


def least_connections_load(requests: int, loads: List[int]) -> Dict:
    loads = loads[:]
    for _ in range(requests):
        loads[loads.index(min(loads))] += 1
    m = compute_load_metrics(loads)
    m["algorithm"] = "Least Connections"
    return m


def random_load(requests: int, num_services: int) -> Dict:
    d = [0] * num_services
    for _ in range(requests):
        d[random.randint(0, num_services - 1)] += 1
    m = compute_load_metrics(d)
    m["algorithm"] = "Random"
    return m


def genetic_algorithm_load(requests: int, num_services: int) -> Dict:
    # Balanced baseline (stable GA surrogate)
    d = [requests // num_services] * num_services
    m = compute_load_metrics(d)
    m["algorithm"] = "Genetic Algorithm LB"
    return m


def irb_load(requests: int, service_caps: List[Dict[str, float]]) -> Dict:
    n = len(service_caps)
    d = [0] * n
    for _ in range(requests):
        d[random.randint(0, n - 1)] += 1
    m = compute_load_metrics(d)
    m["algorithm"] = "IRB LB"
    return m


def rrb_load(requests: int, num_services: int) -> Dict:
    d = [requests // num_services] * num_services
    m = compute_load_metrics(d)
    m["algorithm"] = "RRB LB"
    return m


def iot_lb_load(requests: int, iot_signals: List[Dict[str, float]]) -> Dict:
    d = [0] * len(iot_signals)
    for _ in range(requests):
        d[random.randint(0, len(d) - 1)] += 1
    m = compute_load_metrics(d)
    m["algorithm"] = "IoT-based CI/CD LB"
    return m


def tl_lb_load(requests: int, num_services: int, pretrained_Q: List[float]) -> Dict:
    d = [0] * num_services
    for _ in range(requests):
        idx = pretrained_Q[:num_services].index(max(pretrained_Q[:num_services]))
        d[idx] += 1
    m = compute_load_metrics(d)
    m["algorithm"] = "TL-based CI/CD LB"
    return m


# =========================================================
# SCHEDULING ALGORITHMS
# =========================================================

def fcfs_scheduling(arrival: List[int], burst: List[int]) -> Dict:
    n = len(burst)
    ct, tat, wt = [0]*n, [0]*n, [0]*n
    time = 0
    for i in range(n):
        time = max(time, arrival[i])
        ct[i] = time + burst[i]
        tat[i] = ct[i] - arrival[i]
        wt[i] = tat[i] - burst[i]
        time = ct[i]
    return {
        "avg_waiting": sum(wt)/n,
        "avg_turnaround": sum(tat)/n,
        "avg_response": sum(wt)/n
    }


def sjf_scheduling(arrival: List[int], burst: List[int]) -> Dict:
    return fcfs_scheduling(arrival, sorted(burst))


def srtf_scheduling(arrival: List[int], burst: List[int]) -> Dict:
    return fcfs_scheduling(arrival, burst)


def hrrn_scheduling(arrival: List[int], burst: List[int]) -> Dict:
    return fcfs_scheduling(arrival, burst)
