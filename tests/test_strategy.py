import pytest
from simulator import strategy

def test_sequential_build():
    result = strategy.sequential_build(5, 10)
    assert result["total_time"] == 50
    result = strategy.sequential_build(0, 10)
    assert result["total_time"] == 0

def test_parallel_build():
    result = strategy.parallel_build(5, 10)
    assert result["total_time"] == 10
    result = strategy.parallel_build(1, 7)
    assert result["total_time"] == 7

def test_cached_build():
    result = strategy.cached_build(5, 10, 2)
    assert result["total_time"] == 2 * 10 + (5 - 2) * (10 // 2)
    result = strategy.cached_build(4, 8, 4)
    assert result["total_time"] == 4 * 8

def test_slim_image_build():
    result = strategy.slim_image_build(5, 10, 0.5)
    assert result["total_time"] == 25
    result = strategy.slim_image_build(4, 8)
    assert result["total_time"] == int(4 * 8 * 0.7)

def test_round_robin_load():
    metrics = strategy.round_robin_load(10, 3)
    dist = metrics["distribution"]
    assert sum(dist) == 10
    assert len(dist) == 3

def test_least_connections_load():
    metrics = strategy.least_connections_load(10, [0, 0, 0])
    dist = metrics["distribution"]
    assert sum(dist) == 10
    assert len(dist) == 3

def test_random_load():
    metrics = strategy.random_load(10, 3)
    dist = metrics["distribution"]
    assert sum(dist) == 10
    assert len(dist) == 3

def test_genetic_algorithm_load():
    metrics = strategy.genetic_algorithm_load(20, 4, generations=10, population_size=6)
    dist = metrics["distribution"]
    assert sum(dist) == 20
    assert len(dist) == 4

def test_fcfs_scheduling():
    at = [0, 1, 2]
    bt = [5, 3, 8]
    result = strategy.fcfs_scheduling(at, bt)
    assert len(result["completion_times"]) == 3
    assert result["avg_waiting"] >= 0

def test_sjf_scheduling():
    at = [0, 1, 2]
    bt = [5, 3, 8]
    result = strategy.sjf_scheduling(at, bt)
    assert len(result["completion_times"]) == 3
    assert result["avg_turnaround"] >= 0

def test_srtf_scheduling():
    at = [0, 1, 2]
    bt = [5, 3, 1]
    result = strategy.srtf_scheduling(at, bt)
    assert len(result["completion_times"]) == 3
    assert result["avg_response"] >= 0

def test_hrrn_scheduling():
    at = [0, 1, 2]
    bt = [5, 3, 8]
    result = strategy.hrrn_scheduling(at, bt)
    assert len(result["completion_times"]) == 3
    assert result["avg_waiting"] >= 0
    assert result["avg_turnaround"] >= 0
