import pandas as pd
import matplotlib.pyplot as plt
import os


if not os.path.exists("graphs"):
    os.makedirs("graphs")


if not os.path.exists("logs/results.csv"):
    print("⚠️ results.csv not found! Run simulator first.")
    exit()

df = pd.read_csv("logs/results.csv")


build_df = df[df["phase"] == "Build"]

if not build_df.empty:
    plt.figure(figsize=(8, 5))
    plt.plot(build_df["strategy"], build_df["total_time"], marker='o', color="blue", label="Build Time")
    plt.xlabel("Build Strategies")
    plt.ylabel("Total Time")
    plt.title("Build Algorithms Performance")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/build_total_time.png")
    plt.show()

    
    plt.figure(figsize=(8,5))
    plt.plot(build_df["strategy"], build_df["speedup"], marker='s', color="green", label="Speedup")
    plt.xlabel("Build Strategies")
    plt.ylabel("Speedup")
    plt.title("Build Algorithms Speedup")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/build_speedup.png")
    plt.show()

    
    plt.figure(figsize=(8,5))
    plt.plot(build_df["strategy"], build_df["efficiency"], marker='^', color="purple", label="Efficiency")
    plt.xlabel("Build Strategies")
    plt.ylabel("Efficiency")
    plt.title("Build Algorithms Efficiency")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/build_efficiency.png")
    plt.show()

lb_df = df[df["phase"] == "LoadBalancing"]

if not lb_df.empty:
    x_col = "algorithm" if "algorithm" in lb_df.columns else "strategy"

   
    plt.figure(figsize=(8, 5))
    plt.bar(lb_df[x_col], lb_df["avg_load"], color="skyblue", edgecolor="black", label="Average Load")
    plt.xlabel("Load Balancing Algorithms")
    plt.ylabel("Average Load")
    plt.title("Load Balancing Performance")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/load_avg_load.png")
    plt.show()

    
    plt.figure(figsize=(8, 5))
    plt.bar(lb_df[x_col], lb_df["variance"], color="orange", edgecolor="black", label="Variance")
    plt.xlabel("Load Balancing Algorithms")
    plt.ylabel("Variance")
    plt.title("Load Balancing Variance")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/load_variance.png")
    plt.show()

    
    plt.figure(figsize=(8,5))
    plt.bar(lb_df[x_col], lb_df["fairness_index"], color="green", edgecolor="black", label="Fairness Index")
    plt.xlabel("Load Balancing Algorithms")
    plt.ylabel("Fairness Index")
    plt.title("Load Balancing Fairness Index")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/load_fairness.png")
    plt.show()

   
    plt.figure(figsize=(8,5))
    plt.bar(lb_df[x_col], lb_df["load_imbalance"], color="purple", edgecolor="black", label="Load Imbalance")
    plt.xlabel("Load Balancing Algorithms")
    plt.ylabel("Load Imbalance")
    plt.title("Load Balancing Load Imbalance")
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle="--", alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/load_imbalance.png")
    plt.show()

sched_df = df[df["phase"] == "Scheduling"]

if not sched_df.empty:
    plt.figure(figsize=(8, 5))
    plt.plot(sched_df["algorithm"], sched_df["avg_waiting"], marker='o', linestyle='--', color='red', label="Avg Waiting Time", linewidth=2)
    plt.plot(sched_df["algorithm"], sched_df["avg_turnaround"], marker='s', linestyle='-', color='green', label="Avg Turnaround Time", linewidth=2)
    plt.plot(sched_df["algorithm"], sched_df["avg_response"], marker='^', linestyle=':', color='blue', label="Avg Response Time", linewidth=2)
    plt.xlabel("Scheduling Algorithms")
    plt.ylabel("Time")
    plt.title("Scheduling Algorithms Performance")
    plt.xticks(rotation=45)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("graphs/scheduling_times.png")
    plt.show()

   
    plt.figure(figsize=(10,6))
    sched_metrics = ["avg_waiting", "avg_turnaround", "avg_response"]
    sched_df_plot = sched_df.melt(id_vars=["algorithm"], value_vars=sched_metrics, var_name="Metric", value_name="Time")
    plt.bar(sched_df_plot["algorithm"] + "_" + sched_df_plot["Metric"], sched_df_plot["Time"], color=['red','green','blue']*len(sched_df))
    plt.xticks(rotation=45)
    plt.xlabel("Algorithm & Metric")
    plt.ylabel("Time")
    plt.title("Scheduling Algorithms: Combined Metrics")
    plt.tight_layout()
    plt.grid(axis='y', linestyle="--", alpha=0.3)
    plt.savefig("graphs/scheduling_combined.png")
    plt.show()
