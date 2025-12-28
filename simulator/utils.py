import random
import statistics
import csv
import os
from typing import List, Dict, Optional, Sequence, Any

# ============================================================
# GLOBAL CSV HEADERS (CONSISTENT ACROSS PROJECT)
# ============================================================

DEFAULT_CSV_HEADERS = [
    "phase", "strategy", "algorithm",

    # Build metrics
    "total_time", "speedup", "efficiency",

    # Load balancing metrics
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",

    # Scheduling metrics
    "avg_waiting", "avg_turnaround", "avg_response",

    # AI / Advanced metrics (optional)
    "Q_values",          # RRB
    "final_Q",           # TL-LB
    "iot_score",         # IoT-LB
    "transfer_ratio"     # TL effectiveness
]

# ============================================================
# BASIC RANDOM & STATISTICS
# ============================================================

def random_delay(base: int, variation: int = 2, allow_negative: bool = False) -> int:
    delta = random.randint(-variation, variation) if allow_negative else random.randint(0, variation)
    return max(0, base + delta)


def average_load(distribution: Sequence[float]) -> float:
    return sum(distribution) / len(distribution) if distribution else 0.0


def max_load(distribution: Sequence[float]) -> float:
    return max(distribution) if distribution else 0.0


def min_load(distribution: Sequence[float]) -> float:
    return min(distribution) if distribution else 0.0


def variance_load(distribution: Sequence[float]) -> float:
    return statistics.pvariance(distribution) if len(distribution) > 1 else 0.0


def stdev_load(distribution: Sequence[float]) -> float:
    return statistics.pstdev(distribution) if len(distribution) > 1 else 0.0


def fairness_index(distribution: Sequence[float]) -> float:
    """
    Jain's Fairness Index
    """
    if not distribution:
        return 1.0
    total = sum(distribution)
    if total == 0:
        return 1.0
    return (total ** 2) / (len(distribution) * sum(x ** 2 for x in distribution))


def load_imbalance(distribution: Sequence[float]) -> float:
    """
    (max_load / avg_load) - 1
    """
    avg = average_load(distribution)
    return (max_load(distribution) / avg - 1.0) if avg > 0 else 0.0


def speedup(sequential_time: float, parallel_time: float) -> float:
    return sequential_time / parallel_time if parallel_time > 0 else 0.0


def efficiency(sequential_time: float, parallel_time: float, resources: int) -> float:
    if resources <= 0:
        return 0.0
    return speedup(sequential_time, parallel_time) / resources


# ============================================================
# IRB (RESOURCE-AWARE) HELPERS
# ============================================================

def resource_score(cpu_capacity: float,
                   mem_capacity: float,
                   used_cpu: float = 0.0,
                   used_mem: float = 0.0,
                   cpu_weight: float = 1.0,
                   mem_weight: float = 1.0) -> float:
    cpu_avail = max(0.0, cpu_capacity - used_cpu)
    mem_avail = max(0.0, mem_capacity - used_mem)
    return cpu_weight * cpu_avail + mem_weight * mem_avail


# ============================================================
# REINFORCEMENT & TRANSFER LEARNING HELPERS
# ============================================================

def rl_update(Q: List[float],
              idx: int,
              reward: float,
              learning_rate: float = 0.2) -> float:
    Q[idx] = Q[idx] + learning_rate * (reward - Q[idx])
    return Q[idx]


def init_transfer_q(source_q: Sequence[float],
                    target_size: int,
                    transfer_ratio: float = 0.7) -> List[float]:
    """
    Transfer learning initialization for TL-based LB.
    """
    Q = [1.0] * target_size
    for i in range(min(len(source_q), target_size)):
        Q[i] = transfer_ratio * source_q[i] + (1 - transfer_ratio)
    return Q


def transfer_effectiveness(source_q: Sequence[float],
                           final_q: Sequence[float]) -> float:
    """
    Measures how close the learned policy remains to the transferred knowledge.
    """
    if not source_q or not final_q:
        return 0.0
    n = min(len(source_q), len(final_q))
    diff = sum(abs(source_q[i] - final_q[i]) for i in range(n))
    return 1.0 / (1.0 + diff)


# ============================================================
# IOT SIGNAL PROCESSING
# ============================================================

def normalize_signal(value: float, min_val: float, max_val: float) -> float:
    if max_val == min_val:
        return 0.0
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))


def iot_load_score(cpu_usage: float,
                   latency: float,
                   queue_depth: float,
                   w_cpu: float = 0.4,
                   w_latency: float = 0.4,
                   w_queue: float = 0.2) -> float:
    """
    Lower score = better node
    """
    return (
        w_cpu * cpu_usage +
        w_latency * latency +
        w_queue * queue_depth
    )


def aggregate_iot_signals(signals: Dict[str, float]) -> float:
    return sum(signals.values()) / len(signals) if signals else 0.0


# ============================================================
# CSV LOGGING (SAFE & EXTENSIBLE)
# ============================================================

def save_results_csv(result: Dict[str, Any],
                     phase: str,
                     filename: str = "logs/results.csv",
                     headers: Optional[Sequence[str]] = None) -> None:
    headers = list(headers) if headers else list(DEFAULT_CSV_HEADERS)

    if headers[0] != "phase":
        headers = ["phase"] + [h for h in headers if h != "phase"]

    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    file_exists = os.path.exists(filename)

    # Expand headers if new fields appear
    extra = [k for k in result if k not in headers]
    if extra and file_exists:
        with open(filename, "r", newline="") as f:
            reader = csv.reader(f)
            existing = next(reader)
        missing = [k for k in extra if k not in existing]
        if missing:
            rows = []
            with open(filename, "r", newline="") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            new_headers = existing + missing
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=new_headers)
                writer.writeheader()
                for r in rows:
                    writer.writerow({h: r.get(h, "") for h in new_headers})
            headers = new_headers

    with open(filename, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()

        row = {h: "" for h in headers}
        row["phase"] = phase
        for k, v in result.items():
            if k in row:
                row[k] = v
        writer.writerow(row)
