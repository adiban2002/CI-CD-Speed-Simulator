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

# read CSV
df = pd.read_csv(LOG_PATH)

# helper: coerce numeric columns safely
def to_numeric_safe(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# Common numeric columns used across phases
numeric_cols = [
    "total_time", "speedup", "efficiency",
    "avg_load", "max_load", "min_load", "variance",
    "fairness_index", "load_imbalance",
    "avg_waiting", "avg_turnaround", "avg_response"
]
df = to_numeric_safe(df, numeric_cols)

# ---- Build phase plots ----
build_df = df[df["phase"] == "Build"].copy()
if not build_df.empty:
    if "strategy" not in build_df.columns:
        print("Build phase present but 'strategy' column missing. Skipping build plots.")
    else:
        bgrp = build_df.groupby("strategy").mean(numeric_only=True).reset_index()

        if "total_time" in bgrp.columns:
            plt.figure(figsize=(8, 5))
            plt.plot(bgrp["strategy"], bgrp["total_time"], marker="o", label="Build Time")
            plt.xlabel("Build Strategies")
            plt.ylabel("Total Time")
            plt.title("Build Algorithms — Total Time")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, "build_total_time.png"))
            plt.close()

        if "speedup" in bgrp.columns:
            plt.figure(figsize=(8, 5))
            plt.plot(bgrp["strategy"], bgrp["speedup"], marker="s", label="Speedup")
            plt.xlabel("Build Strategies")
            plt.ylabel("Speedup")
            plt.title("Build Algorithms — Speedup")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, "build_speedup.png"))
            plt.close()

        if "efficiency" in bgrp.columns:
            plt.figure(figsize=(8, 5))
            plt.plot(bgrp["strategy"], bgrp["efficiency"], marker="^", label="Efficiency")
            plt.xlabel("Build Strategies")
            plt.ylabel("Efficiency")
            plt.title("Build Algorithms — Efficiency")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.6)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, "build_efficiency.png"))
            plt.close()
else:
    print("No Build phase data found in results.csv — skipping build plots.")

# ---- Load Balancing phase plots ----
lb_df = df[df["phase"] == "LoadBalancing"].copy()
if not lb_df.empty:
    x_col = "algorithm" if "algorithm" in lb_df.columns else "strategy"
    if x_col not in lb_df.columns:
        print("LoadBalancing phase present but neither 'algorithm' nor 'strategy' columns exist. Skipping LB plots.")
    else:
        lb_grp = lb_df.groupby(x_col).mean(numeric_only=True).reset_index()

        def bar_plot(x, y, fname, ylabel, title):
            if y in lb_grp.columns:
                plt.figure(figsize=(8, 5))
                plt.bar(lb_grp[x], lb_grp[y], edgecolor="black")
                plt.xlabel("Load Balancing Algorithms")
                plt.ylabel(ylabel)
                plt.title(title)
                plt.xticks(rotation=45, ha="right")
                plt.grid(axis="y", linestyle="--", alpha=0.6)
                plt.tight_layout()
                plt.savefig(os.path.join(GRAPHS_DIR, fname))
                plt.close()

        bar_plot(x_col, "avg_load", "load_avg_load.png", "Average Load", "Load Balancing — Average Load")
        bar_plot(x_col, "variance", "load_variance.png", "Variance", "Load Balancing — Variance")
        bar_plot(x_col, "fairness_index", "load_fairness.png", "Fairness Index", "Load Balancing — Fairness Index")
        bar_plot(x_col, "load_imbalance", "load_imbalance.png", "Load Imbalance", "Load Balancing — Load Imbalance")

        # --- Extra plots for IRB and RRB if present ---
        # IRB: expect a column named "service_capacities_summary" containing a list of dicts per run
        if "service_capacities_summary" in lb_df.columns:
            irb_rows = lb_df[lb_df["algorithm"].str.contains("IRB", na=False) | lb_df["algorithm"].str.contains("Instance Resource", na=False)]
            if not irb_rows.empty:
                # parse lists of dicts, aggregate per-instance CPU and MEM capacities across runs
                cpu_caps_list = []  # list of lists
                mem_caps_list = []
                for val in irb_rows["service_capacities_summary"].dropna().unique():
                    try:
                        parsed = ast.literal_eval(val) if isinstance(val, str) else val
                        if isinstance(parsed, list) and parsed:
                            cpu_caps = [float(d.get("cpu_capacity", 0)) for d in parsed]
                            mem_caps = [float(d.get("mem_capacity", 0)) for d in parsed]
                            cpu_caps_list.append(cpu_caps)
                            mem_caps_list.append(mem_caps)
                    except Exception:
                        continue

                # pad arrays to equal length and compute mean across runs per instance index
                if cpu_caps_list:
                    max_len = max(len(l) for l in cpu_caps_list)
                    cpu_arr = np.array([l + [np.nan] * (max_len - len(l)) for l in cpu_caps_list], dtype=float)
                    mem_arr = np.array([l + [np.nan] * (max_len - len(l)) for l in mem_caps_list], dtype=float)
                    cpu_mean = np.nanmean(cpu_arr, axis=0)
                    mem_mean = np.nanmean(mem_arr, axis=0)
                    indices = list(range(len(cpu_mean)))

                    plt.figure(figsize=(8,5))
                    plt.plot(indices, cpu_mean, marker='o', label='CPU Capacity (avg)')
                    plt.plot(indices, mem_mean, marker='s', label='Memory Capacity (avg)')
                    plt.xlabel("Instance Index")
                    plt.ylabel("Capacity (units)")
                    plt.title("IRB — Average Instance Capacities (across runs)")
                    plt.xticks(indices)
                    plt.legend()
                    plt.grid(True, linestyle="--", alpha=0.6)
                    plt.tight_layout()
                    plt.savefig(os.path.join(GRAPHS_DIR, "irb_instance_capacities.png"))
                    plt.close()

        # RRB: expect columns "Q_values" and/or "base_response_characteristics"
        if "Q_values" in lb_df.columns or "base_response_characteristics" in lb_df.columns:
            rrb_rows = lb_df[lb_df["algorithm"].str.contains("RRB", na=False) | lb_df[lb_df["algorithm"].fillna("").str.contains("Reinforcement", na=False)]["algorithm"].notna()]
            # fallback: include entries that have Q_values or base_response_characteristics even if algorithm name differs
            if rrb_rows.empty:
                rrb_rows = lb_df[lb_df["Q_values"].notna() | lb_df["base_response_characteristics"].notna()]

            # parse Q_values
            q_list_all = []
            base_resp_all = []
            for _, row in rrb_rows.iterrows():
                if "Q_values" in row and pd.notna(row["Q_values"]):
                    try:
                        parsed = ast.literal_eval(row["Q_values"]) if isinstance(row["Q_values"], str) else row["Q_values"]
                        if isinstance(parsed, (list, tuple)):
                            q_list_all.append([float(x) for x in parsed])
                    except Exception:
                        pass
                if "base_response_characteristics" in row and pd.notna(row["base_response_characteristics"]):
                    try:
                        parsed = ast.literal_eval(row["base_response_characteristics"]) if isinstance(row["base_response_characteristics"], str) else row["base_response_characteristics"]
                        if isinstance(parsed, (list, tuple)):
                            base_resp_all.append([float(x) for x in parsed])
                    except Exception:
                        pass

            # plot averaged Q-values per service index
            if q_list_all:
                max_len = max(len(l) for l in q_list_all)
                q_arr = np.array([l + [np.nan] * (max_len - len(l)) for l in q_list_all], dtype=float)
                q_mean = np.nanmean(q_arr, axis=0)
                idx = list(range(len(q_mean)))
                plt.figure(figsize=(8,5))
                plt.plot(idx, q_mean, marker='o', linestyle='-', label='Avg Q-value')
                plt.xlabel("Service Index")
                plt.ylabel("Q-value")
                plt.title("RRB — Average Final Q-values (across runs)")
                plt.xticks(idx)
                plt.grid(True, linestyle="--", alpha=0.6)
                plt.tight_layout()
                plt.savefig(os.path.join(GRAPHS_DIR, "rrb_q_values.png"))
                plt.close()

            # plot averaged base response characteristics per service index
            if base_resp_all:
                max_len = max(len(l) for l in base_resp_all)
                b_arr = np.array([l + [np.nan] * (max_len - len(l)) for l in base_resp_all], dtype=float)
                b_mean = np.nanmean(b_arr, axis=0)
                idx = list(range(len(b_mean)))
                plt.figure(figsize=(8,5))
                plt.plot(idx, b_mean, marker='s', linestyle='-', label='Avg Base Response')
                plt.xlabel("Service Index")
                plt.ylabel("Base Response Time")
                plt.title("RRB — Average Base Response Characteristics (across runs)")
                plt.xticks(idx)
                plt.grid(True, linestyle="--", alpha=0.6)
                plt.tight_layout()
                plt.savefig(os.path.join(GRAPHS_DIR, "rrb_base_response.png"))
                plt.close()
else:
    print("No LoadBalancing phase data found in results.csv — skipping LB plots.")

# ---- Scheduling phase plots ----
sched_df = df[df["phase"] == "Scheduling"].copy()
if not sched_df.empty:
    if "algorithm" not in sched_df.columns:
        print("Scheduling phase present but 'algorithm' column missing. Skipping scheduling plots.")
    else:
        sched_grp = sched_df.groupby("algorithm").mean(numeric_only=True).reset_index()
        metrics = []
        for c in ["avg_waiting", "avg_turnaround", "avg_response"]:
            if c in sched_grp.columns:
                metrics.append(c)

        if metrics:
            plt.figure(figsize=(9, 6))
            markers = ["o", "s", "^"]
            linestyles = ["--", "-", ":"]
            for i, col in enumerate(metrics):
                plt.plot(sched_grp["algorithm"], sched_grp[col], marker=markers[i % len(markers)],
                         linestyle=linestyles[i % len(linestyles)], linewidth=2, label=col)
            plt.xlabel("Scheduling Algorithms")
            plt.ylabel("Time")
            plt.title("Scheduling Algorithms — Average Times")
            plt.xticks(rotation=45, ha="right")
            plt.grid(True, linestyle="--", alpha=0.3)
            plt.legend()
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, "scheduling_times.png"))
            plt.close()

        combined_metrics = [c for c in ["avg_waiting", "avg_turnaround", "avg_response"] if c in sched_grp.columns]
        if combined_metrics:
            melted = sched_grp.melt(id_vars=["algorithm"], value_vars=combined_metrics,
                                     var_name="Metric", value_name="Time")
            pivot = melted.pivot(index="algorithm", columns="Metric", values="Time").fillna(0)
            pivot.plot(kind="bar", figsize=(10, 6))
            plt.xlabel("Algorithm")
            plt.ylabel("Time")
            plt.title("Scheduling Algorithms — Combined Metrics")
            plt.xticks(rotation=45, ha="right")
            plt.grid(axis="y", linestyle="--", alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(GRAPHS_DIR, "scheduling_combined.png"))
            plt.close()
else:
    print("No Scheduling phase data found in results.csv — skipping scheduling plots.")

print(f"Graphs saved to '{GRAPHS_DIR}' (if any).")
