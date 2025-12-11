import random
import statistics
import csv
import os
from typing import List, Dict, Iterable, Optional, Sequence, Any

# Default CSV header used across the project (keeps logs consistent)
DEFAULT_CSV_HEADERS = [
    "phase", "strategy", "algorithm",
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response"
]


def random_delay(base: int, variation: int = 2, allow_negative: bool = False) -> int:
    """
    Return an integer delay around `base` with up to `variation` randomness.
    If allow_negative is False, result is at least 0.
    """
    if allow_negative:
        return max(0, base + random.randint(-variation, variation))
    return max(0, base + random.randint(0, variation))


def average_load(distribution: Sequence[float]) -> float:
    """Population average (mean) of the distribution; returns 0 for empty input."""
    if not distribution:
        return 0.0
    return float(sum(distribution)) / float(len(distribution))


def max_load(distribution: Sequence[float]) -> float:
    """Maximum value in distribution or 0 for empty."""
    return float(max(distribution)) if distribution else 0.0


def min_load(distribution: Sequence[float]) -> float:
    """Minimum value in distribution or 0 for empty."""
    return float(min(distribution)) if distribution else 0.0


def variance_load(distribution: Sequence[float]) -> float:
    """
    Population variance for the distribution (statistics.pvariance).
    Returns 0 for empty or single-element input.
    """
    if len(distribution) <= 1:
        return 0.0
    return float(statistics.pvariance(distribution))


def stdev_load(distribution: Sequence[float]) -> float:
    """Population standard deviation (sqrt of pvariance)."""
    if len(distribution) <= 1:
        return 0.0
    return float(statistics.pvariance(distribution) ** 0.5)


def fairness_index(distribution: Sequence[float]) -> float:
    """
    Jain's fairness index:
    (sum(x))^2 / (n * sum(x^2))
    Returns 1.0 when distribution is empty or all zeros (treated as perfectly fair).
    """
    if not distribution:
        return 1.0
    total = float(sum(distribution))
    if total == 0.0:
        return 1.0
    n = len(distribution)
    sum_sq = float(sum(x ** 2 for x in distribution))
    if sum_sq == 0.0:
        return 1.0
    return (total ** 2) / (n * sum_sq)


def load_imbalance(distribution: Sequence[float]) -> float:
    """
    A simple imbalance metric: (max_load / avg_load) - 1
    Returns 0.0 for empty distributions or when avg_load is zero.
    """
    if not distribution:
        return 0.0
    avg = average_load(distribution)
    if avg == 0:
        return 0.0
    return float(max_load(distribution) / avg - 1.0)


def speedup(sequential_time: float, parallel_time: float) -> float:
    """Compute speedup = T_seq / T_parallel (safe guard for zero)."""
    try:
        return float(sequential_time) / float(parallel_time) if float(parallel_time) > 0 else 0.0
    except (TypeError, ValueError):
        return 0.0


def efficiency(sequential_time: float, parallel_time: float, resources: int) -> float:
    """
    Efficiency = speedup / resources.
    Returns 0 on invalid inputs.
    """
    if resources <= 0:
        return 0.0
    sp = speedup(sequential_time, parallel_time)
    return float(sp) / float(resources) if resources > 0 else 0.0


def normalize_distribution(distribution: Sequence[float]) -> List[float]:
    """
    Convert any sequence to a list of floats (useful before numeric ops).
    """
    return [float(x) for x in distribution]


# --- Helpers useful for IRB / RRB algorithms ---

def resource_score(cpu_capacity: float, mem_capacity: float,
                   used_cpu: float = 0.0, used_mem: float = 0.0,
                   cpu_weight: float = 1.0, mem_weight: float = 1.0) -> float:
    """
    Compute a weighted resource availability score for an instance.
    Example usage in IRB:
        score = resource_score(cpu_cap, mem_cap, used_cpu, used_mem, cpu_weight=1.0, mem_weight=1.0)
    Higher score means more available capacity.
    """
    cpu_avail = max(0.0, float(cpu_capacity) - float(used_cpu))
    mem_avail = max(0.0, float(mem_capacity) - float(used_mem))
    return cpu_weight * cpu_avail + mem_weight * mem_avail


def rl_update(Q: List[float], idx: int, reward: float, learning_rate: float = 0.2) -> float:
    """
    One-step Q-value update:
        Q[idx] = Q[idx] + lr * (reward - Q[idx])
    Returns the updated Q[idx]. Mutates the provided Q list.
    """
    if not (0 <= idx < len(Q)):
        raise IndexError("rl_update: idx out of range")
    try:
        q_old = float(Q[idx])
        r = float(reward)
        lr = float(learning_rate)
    except (TypeError, ValueError):
        return Q[idx]

    q_new = q_old + lr * (r - q_old)
    Q[idx] = q_new
    return q_new


# --- CSV logging helper (improved) ---

def save_results_csv(result: Dict[str, Any],
                     phase: str,
                     filename: str = "logs/results.csv",
                     headers: Optional[Sequence[str]] = None) -> None:
    """
    Append a result row to CSV (creates file and headers if not present).

    - result: mapping of column_name -> value for the run (can contain subset of headers)
    - phase: top-level phase string (e.g., "Build", "LoadBalancing", "Scheduling")
    - filename: path to CSV file
    - headers: optional header list; if not provided DEFAULT_CSV_HEADERS used

    The function will:
      - create parent directory if needed
      - write a consistent header (headers param or DEFAULT_CSV_HEADERS)
      - fill missing columns with empty string
    """
    headers = list(headers) if headers is not None else DEFAULT_CSV_HEADERS
    # Guarantee phase is the first header
    if headers[0] != "phase":
        headers = ["phase"] + [h for h in headers if h != "phase"]

    # ensure directory exists
    dirpath = os.path.dirname(filename) or "."
    os.makedirs(dirpath, exist_ok=True)

    write_header = not os.path.exists(filename)

    # prepare row following the header order
    row = {h: "" for h in headers}
    row["phase"] = phase
    for k, v in result.items():
        if k in row:
            row[k] = v
        else:
            # If result contains keys outside headers, append them as well (extend headers)
            row[k] = v

    # If there are keys outside headers, we need to rewrite header to include them.
    extra_keys = [k for k in result.keys() if k not in headers]
    if extra_keys and not write_header:
        # read existing header to see if rewrite needed
        try:
            with open(filename, newline="", mode="r") as rfile:
                existing = csv.reader(rfile)
                existing_header = next(existing, None)
        except Exception:
            existing_header = None

        if existing_header is not None:
            # if existing header doesn't contain extras, rewrite file with extended header
            missing = [k for k in extra_keys if k not in existing_header]
            if missing:
                new_headers = list(existing_header) + missing
                # read existing rows
                with open(filename, newline="", mode="r") as rfile:
                    reader = csv.DictReader(rfile)
                    rows = list(reader)
                # write back with new headers
                with open(filename, newline="", mode="w") as wfile:
                    writer = csv.DictWriter(wfile, fieldnames=new_headers)
                    writer.writeheader()
                    for r in rows:
                        # ensure all keys exist
                        out = {h: r.get(h, "") for h in new_headers}
                        writer.writerow(out)
                write_header = False
                headers = new_headers

    # finally append (open in append mode)
    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        if write_header:
            writer.writeheader()
        # ensure the row contains exactly header keys (extra keys ignored here)
        outrow = {h: row.get(h, "") for h in headers}
        writer.writerow(outrow)
