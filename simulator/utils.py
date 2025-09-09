import random
import statistics
import csv
import os
from typing import List, Dict


def random_delay(base: int, variation: int = 2, allow_negative: bool = False) -> int:
    if allow_negative:
        return max(0, base + random.randint(-variation, variation))
    return base + random.randint(0, variation)


def average_load(distribution: List[int]) -> float:
    return sum(distribution) / len(distribution) if distribution else 0


def max_load(distribution: List[int]) -> int:
    return max(distribution) if distribution else 0


def min_load(distribution: List[int]) -> int:
    return min(distribution) if distribution else 0


def variance_load(distribution: List[int]) -> float:
    return statistics.variance(distribution) if len(distribution) > 1 else 0


def stdev_load(distribution: List[int]) -> float:
    return statistics.stdev(distribution) if len(distribution) > 1 else 0


def fairness_index(distribution: List[int]) -> float:
    if not distribution or sum(distribution) == 0:
        return 1.0
    numerator = (sum(distribution)) ** 2
    denominator = len(distribution) * sum(x ** 2 for x in distribution)
    return numerator / denominator


def load_imbalance(distribution: List[int]) -> float:
    if not distribution:
        return 0.0
    avg = average_load(distribution)
    if avg == 0:
        return 0.0
    return (max_load(distribution) / avg) - 1

def speedup(sequential_time: float, parallel_time: float) -> float:
    return sequential_time / parallel_time if parallel_time > 0 else 0


def efficiency(sequential_time: float, parallel_time: float, resources: int) -> float:
    if parallel_time <= 0 or resources <= 0:
        return 0
    return speedup(sequential_time, parallel_time) / resources


def save_results_csv(result: Dict, phase: str, filename: str = "logs/results.csv") -> None:
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    write_header = not os.path.exists(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["phase"] + list(result.keys()))

        if write_header:
            writer.writeheader()

       
        row = {"phase": phase}
        row.update(result)
        writer.writerow(row)
