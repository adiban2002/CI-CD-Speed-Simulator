import pytest
from unittest.mock import patch
from simulator import build_simulator


def test_build_phase_sequential():
    with patch("builtins.input", side_effect=["3", "5", "1"]):
        build_simulator.build_phase()

def test_build_phase_parallel():
    with patch("builtins.input", side_effect=["4", "6", "2"]):
        build_simulator.build_phase()

def test_build_phase_cached():
    with patch("builtins.input", side_effect=["5", "10", "3", "2"]):
        build_simulator.build_phase()

def test_build_phase_slim():
    with patch("builtins.input", side_effect=["5", "8", "4", "0.6"]):
        build_simulator.build_phase()



def test_load_phase_round_robin():
    with patch("builtins.input", side_effect=["3", "10", "1"]):
        build_simulator.load_balancing_phase()

def test_load_phase_least_connections():
    with patch("builtins.input", side_effect=["4", "12", "2"]):
        build_simulator.load_balancing_phase()

def test_load_phase_random():
    with patch("builtins.input", side_effect=["3", "8", "3"]):
        build_simulator.load_balancing_phase()

def test_load_phase_genetic():
    with patch("builtins.input", side_effect=["4", "15", "4"]):
        build_simulator.load_balancing_phase()



def test_scheduling_phase_fcfs():
    with patch("builtins.input", side_effect=[
        "3",                 
        "0", "5",            
        "1", "3",           
        "2", "8",            
        "1"                  
    ]):
        build_simulator.scheduling_phase()

def test_scheduling_phase_sjf():
    with patch("builtins.input", side_effect=[
        "3",
        "0", "5",
        "1", "3",
        "2", "8",
        "2"                  
    ]):
        build_simulator.scheduling_phase()

def test_scheduling_phase_srtf():
    with patch("builtins.input", side_effect=[
        "3",
        "0", "5",
        "1", "3",
        "2", "1",
        "3"                   
    ]):
        build_simulator.scheduling_phase()

def test_scheduling_phase_hrrn():
    with patch("builtins.input", side_effect=[
        "3",                 
        "0", "5",            
        "1", "3",           
        "2", "8",            
        "4"                  
    ]):
        build_simulator.scheduling_phase()
