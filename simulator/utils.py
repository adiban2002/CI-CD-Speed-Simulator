import random
import statistics
import csv
import os
from typing import List, Dict, Iterable, Optional, Sequence, Any

# ============================================================
# CSV HEADERS (GLOBAL CONSISTENCY)
# ============================================================
DEFAULT_CSV_HEADERS = [
    "phase", "strategy", "algorithm",
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response",
    # Advanced / AI fields (optional, auto-added if used)
    "Q_values", "final_Q",
    "iot_score", "iot_signals",
    "transfer_ratio"
]

# ============================================================
# BASIC RANDOM & STATISTICAL UTILITIES
# ============================================================

def random_delay(base: int, variation: int = 2, allow_negative: bool = False) -> int:
    if allow_negative:
        return max(0, base + random.randint(-variation, variation))
    return max(0, base + random.randint(0, variation))


def average_load(distribution: Sequence[float]) -> float:
    return float(sum(distribution)) / float(len(distribution)) if distribution else 0.0


def max_load(distribution: Sequence[float]) -> float:
    return float(max(distribution)) if distribution else 0.0


def min_load(distribution: Sequence[float]) -> float:
    return float(min(distribution)) if distribution else 0.0


def variance_load(distribution: Sequence[float]) -> float:
    if len(distribution) <= 1:
        return 0.0
    return float(statistics.pvariance(distribution))


def stdev_load(distribution: Sequence[float]) -> float:
    if len(distribution) <= 1:
        return 0.0
    return float(statistics.pvariance(distribution) ** 0.5)


def fairness_index(distribution: Sequence[float]) -> float:
    if not distribution:
        return 1.0
    total = float(sum(distribution))
    if total == 0:
        return 1.0
    n = len(distribution)
    sum_sq = float(sum(x ** 2 for x in distribution))
    if sum_sq == 0:
        return 1.0
    return (total ** 2) / (n * sum_sq)


def load_imbalance(distribution: Sequence[float]) -> float:
    if not distribution:
        return 0.0
    avg = average_load(distribution)
    if avg == 0:
        return 0.0
    return float(max_load(distribution) / avg - 1.0)


def speedup(sequential_time: float, parallel_time: float) -> float:
    try:
        return float(sequential_time) / float(parallel_time) if parallel_time > 0 else 0.0
    except (TypeError, ValueError):
        return 0.0


def efficiency(sequential_time: float, parallel_time: float, resources: int) -> float:
    if resources <= 0:
        return 0.0
    return speedup(sequential_time, parallel_time) / float(resources)

# ============================================================
# IRB (RESOURCE-AWARE) HELPERS
# ============================================================

def resource_score(cpu_capacity: float, mem_capacity: float,
                   used_cpu: float = 0.0, used_mem: float = 0.0,
                   cpu_weight: float = 1.0, mem_weight: float = 1.0) -> float:
    cpu_avail = max(0.0, float(cpu_capacity) - float(used_cpu))
    mem_avail = max(0.0, float(mem_capacity) - float(used_mem))
    return cpu_weight * cpu_avail + mem_weight * mem_avail

# ============================================================
# REINFORCEMENT / TL HELPERS
# ============================================================

def rl_update(Q: List[float], idx: int, reward: float,
              learning_rate: float = 0.2) -> float:
    if not (0 <= idx < len(Q)):
        raise IndexError("rl_update: idx out of range")
    q_old = float(Q[idx])
    q_new = q_old + learning_rate * (float(reward) - q_old)
    Q[idx] = q_new
    return q_new


def init_transfer_q(source_q: Sequence[float],
                    target_size: int,
                    transfer_ratio: float = 0.7) -> List[float]:
    """
    Initialize Q-values for TL-based LB using transferred knowledge.

    transfer_ratio ∈ [0,1]:
      1.0 → full transfer
      0.0 → no transfer (cold start)
    """
    target_q = [1.0] * target_size
    for i in range(min(len(source_q), target_size)):
        target_q[i] = transfer_ratio * float(source_q[i]) + (1 - transfer_ratio) * 1.0
    return target_q


def transfer_effectiveness(source_q: Sequence[float],
                           target_q: Sequence[float]) -> float:
    """
    Measures how much transferred knowledge influenced the final policy.
    """
    if not source_q or not target_q:
        return 0.0
    n = min(len(source_q), len(target_q))
    diff = sum(abs(float(source_q[i]) - float(target_q[i])) for i in range(n))
    return 1.0 / (1.0 + diff)

# ============================================================
# IOT-BASED SIGNAL PROCESSING HELPERS
# ============================================================

def normalize_signal(value: float,
                     min_val: float,
                     max_val: float) -> float:
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
    Compute a composite IoT-aware load score.
    Lower score ⇒ better candidate for load assignment.
    """
    return (
        w_cpu * cpu_usage +
        w_latency * latency +
        w_queue * queue_depth
    )


def aggregate_iot_signals(signals: Dict[str, float]) -> float:
    """
    Aggregate arbitrary IoT signals into a single score.
    """
    if not signals:
        return 0.0
    return sum(float(v) for v in signals.values()) / len(signals)

# ============================================================
# CSV LOGGING (ROBUST, EXTENSIBLE)
# ============================================================

def save_results_csv(result: Dict[str, Any],
                     phase: str,
                     filename: str = "logs/results.csv",
                     headers: Optional[Sequence[str]] = None) -> None:

    headers = list(headers) if headers is not None else DEFAULT_CSV_HEADERS

    if headers[0] != "phase":
        headers = ["phase"] + [h for h in headers if h != "phase"]

    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    file_exists = os.path.exists(filename)

    # Expand headers dynamically if new keys appear
    extra_keys = [k for k in result.keys() if k not in headers]
    if extra_keys and file_exists:
        with open(filename, newline="", mode="r") as rf:
            reader = csv.reader(rf)
            existing_header = next(reader, headers)
        missing = [k for k in extra_keys if k not in existing_header]
        if missing:
            rows = []
            with open(filename, newline="", mode="r") as rf:
                reader = csv.DictReader(rf)
                rows = list(reader)
            new_headers = list(existing_header) + missing
            with open(filename, newline="", mode="w") as wf:
                writer = csv.DictWriter(wf, fieldnames=new_headers)
                writer.writeheader()
                for r in rows:
                    writer.writerow({h: r.get(h, "") for h in new_headers})
            headers = new_headers

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        row = {h: "" for h in headers}
        row["phase"] = phase
        for k, v in result.items():
            if k in row:
                row[k] = v
        writer.writerow(row)
