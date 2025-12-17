import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import ast
import numpy as np

GRAPHS_DIR = "graphs"
LOG_PATH = "logs/results.csv"

os.makedirs(GRAPHS_DIR, exist_ok=True)

if not os.path.exists(LOG_PATH):
    print("⚠️ results.csv not found! Run simulator first.")
    sys.exit(1)

df = pd.read_csv(LOG_PATH)

# -----------------------------
# Helpers
# -----------------------------
def to_numeric_safe(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

numeric_cols = [
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response"
]
df = to_numeric_safe(df, numeric_cols)

# =====================================================
# BUILD PHASE
# =====================================================
build_df = df[df["phase"] == "Build"].copy()
if not build_df.empty and "strategy" in build_df.columns:
    bgrp = build_df.groupby("strategy").mean(numeric_only=True).reset_index()

    for metric, fname, ylabel in [
        ("total_time", "build_total_time.png", "Total Time"),
        ("speedup", "build_speedup.png", "Speedup"),
        ("efficiency", "build_efficiency.png", "Efficiency"),
    ]:
        if metric in bgrp.columns:
            plt.figure(figsize=(8, 5))
            plt.plot(bgrp["strategy"], bgrp[metric], marker="o")
            plt.xlabel("Build Strategy")
            plt.ylabel(ylabel)
            plt.title(f"Build Algorithms — {ylabel}")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, fname))
            plt.close()

# =====================================================
# LOAD BALANCING PHASE (ALL ALGORITHMS)
# =====================================================
lb_df = df[df["phase"] == "LoadBalancing"].copy()
if not lb_df.empty and "algorithm" in lb_df.columns:
    lb_grp = lb_df.groupby("algorithm").mean(numeric_only=True).reset_index()

    def bar_plot(metric, fname, ylabel):
        if metric in lb_grp.columns:
            plt.figure(figsize=(9, 5))
            plt.bar(lb_grp["algorithm"], lb_grp[metric], edgecolor="black")
            plt.xlabel("Load Balancing Algorithm")
            plt.ylabel(ylabel)
            plt.title(f"Load Balancing — {ylabel}")
            plt.xticks(rotation=45, ha="right")
            plt.grid(axis="y", linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, fname))
            plt.close()

    bar_plot("avg_load", "lb_avg_load.png", "Average Load")
    bar_plot("variance", "lb_variance.png", "Variance")
    bar_plot("fairness_index", "lb_fairness.png", "Fairness Index")
    bar_plot("load_imbalance", "lb_imbalance.png", "Load Imbalance")

# =====================================================
# IRB — RESOURCE CAPACITY ANALYSIS
# =====================================================
if "service_capacities_summary" in lb_df.columns:
    irb_rows = lb_df[lb_df["algorithm"].str.contains("IRB", na=False)]
    cpu_all, mem_all = [], []

    for val in irb_rows["service_capacities_summary"].dropna():
        try:
            parsed = ast.literal_eval(val)
            cpu_all.append([d["cpu_capacity"] for d in parsed])
            mem_all.append([d["mem_capacity"] for d in parsed])
        except Exception:
            pass

    if cpu_all:
        max_len = max(len(x) for x in cpu_all)
        cpu_arr = np.array([x + [np.nan]*(max_len-len(x)) for x in cpu_all])
        mem_arr = np.array([x + [np.nan]*(max_len-len(x)) for x in mem_all])

        plt.figure(figsize=(8,5))
        plt.plot(np.nanmean(cpu_arr, axis=0), marker="o", label="CPU Capacity")
        plt.plot(np.nanmean(mem_arr, axis=0), marker="s", label="Memory Capacity")
        plt.xlabel("Instance Index")
        plt.ylabel("Capacity")
        plt.title("IRB LB — Average Instance Capacities")
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHS_DIR, "irb_capacity.png"))
        plt.close()

# =====================================================
# RRB & TL — Q-VALUE ANALYSIS
# =====================================================
def plot_q_values(rows, fname, title):
    q_all = []
    for v in rows.dropna():
        try:
            parsed = ast.literal_eval(v)
            q_all.append(parsed)
        except Exception:
            pass

    if q_all:
        max_len = max(len(x) for x in q_all)
        q_arr = np.array([x + [np.nan]*(max_len-len(x)) for x in q_all])
        plt.figure(figsize=(8,5))
        plt.plot(np.nanmean(q_arr, axis=0), marker="o")
        plt.xlabel("Service Index")
        plt.ylabel("Q-value")
        plt.title(title)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.savefig(os.path.join(GRAPHS_DIR, fname))
        plt.close()

if "Q_values" in lb_df.columns:
    rrb_rows = lb_df[lb_df["algorithm"].str.contains("RRB", na=False)]["Q_values"]
    plot_q_values(rrb_rows, "rrb_q_values.png", "RRB — Average Final Q-Values")

if "final_Q" in lb_df.columns:
    tl_rows = lb_df[lb_df["algorithm"].str.contains("TL", na=False)]["final_Q"]
    plot_q_values(tl_rows, "tl_q_values.png", "TL-LB — Transferred & Adapted Q-Values")

# =====================================================
# IOT-LB — SIGNAL SENSITIVITY ANALYSIS
# =====================================================
iot_rows = lb_df[lb_df["algorithm"].str.contains("IoT", na=False)]
if not iot_rows.empty:
    plt.figure(figsize=(8,5))
    plt.scatter(iot_rows["variance"], iot_rows["fairness_index"], alpha=0.7)
    plt.xlabel("Variance")
    plt.ylabel("Fairness Index")
    plt.title("IoT-LB — Variance vs Fairness")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "iot_variance_vs_fairness.png"))
    plt.close()

# =====================================================
# SCHEDULING PHASE
# =====================================================
sched_df = df[df["phase"] == "Scheduling"].copy()
if not sched_df.empty and "algorithm" in sched_df.columns:
    sgrp = sched_df.groupby("algorithm").mean(numeric_only=True).reset_index()

    plt.figure(figsize=(9,6))
    for col, style in zip(["avg_waiting", "avg_turnaround", "avg_response"], ["o", "s", "^"]):
        if col in sgrp.columns:
            plt.plot(sgrp["algorithm"], sgrp[col], marker=style, label=col)

    plt.xlabel("Scheduling Algorithm")
    plt.ylabel("Time")
    plt.title("Scheduling Algorithms — Average Times")
    plt.xticks(rotation=45, ha="right")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(GRAPHS_DIR, "scheduling_times.png"))
    plt.close()

print(f"✅ Graphs generated in '{GRAPHS_DIR}/'")
