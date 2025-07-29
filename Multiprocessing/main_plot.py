import random
import time
import argparse
import os
import threading
import psutil
import matplotlib.pyplot as plt
import numpy as np

cpu_per_core_usage = []
timestamps = []
monitoring_flag = False

def estimate_nbr_points_in_quarter_circle(nbr_estimates):
    print(f"Executing estimate_nbr_points_in_quarter_circle with {nbr_estimates:,} samples on pid {os.getpid()}")
    nbr_trials_in_quarter_unit_circle = 0
    for _ in range(int(nbr_estimates)):
        x = random.uniform(0, 1)
        y = random.uniform(0, 1)
        is_in_unit_circle = x * x + y * y <= 1.0
        nbr_trials_in_quarter_unit_circle += is_in_unit_circle
    return nbr_trials_in_quarter_unit_circle

def monitor_cpu_usage(interval=0.5):
    """Monitor per-core CPU usage every `interval` seconds."""
    global monitoring_flag
    while monitoring_flag:
        usage = psutil.cpu_percent(interval=interval, percpu=True)  # List of % per core
        cpu_per_core_usage.append(usage)
        timestamps.append(time.time() - start_time)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Estimate Pi using Monte Carlo method.')
    parser.add_argument('nbr_workers', type=int, help='Number of workers')
    parser.add_argument('--nbr_samples_in_total', type=int, default=int(1e8), help='Total number of samples')
    parser.add_argument('--processes', action="store_true", help='Use processes instead of threads')
    args = parser.parse_args()

    if args.processes:
        print("Using Processes")
        from multiprocessing import Pool
    else:
        print("Using Threads")
        from multiprocessing.dummy import Pool

    nbr_samples_in_total = args.nbr_samples_in_total
    nbr_parallel_blocks = args.nbr_workers
    pool = Pool(processes=nbr_parallel_blocks)
    nbr_samples_per_worker = nbr_samples_in_total / nbr_parallel_blocks
    nbr_trials_per_worker = [nbr_samples_per_worker] * nbr_parallel_blocks

    monitoring_flag = True
    start_time = time.time()
    monitor_thread = threading.Thread(target=monitor_cpu_usage)
    monitor_thread.start()

    try:
        t1 = time.time()
        nbr_in_quarter_unit_circles = pool.map(estimate_nbr_points_in_quarter_circle, nbr_trials_per_worker)
        pi_estimate = sum(nbr_in_quarter_unit_circles) * 4 / float(nbr_samples_in_total)
        elapsed_time = time.time() - t1
        print("\nEstimated pi:", pi_estimate)
        print("Elapsed Time:", elapsed_time, "seconds")
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected! Terminating workers...")
        pool.terminate()
        pool.join()
        monitoring_flag = False
        monitor_thread.join()
        exit(1)
    else:
        pool.close()
        pool.join()

    monitoring_flag = False
    monitor_thread.join()

    # Convert list of per-core usages to numpy array for plotting
    cpu_per_core_usage = np.array(cpu_per_core_usage)  # shape: (time_steps, cores)
    timestamps = np.array(timestamps)

    # Plotting CPU Usage Heatmap
    plt.figure(figsize=(12, 6))
    plt.imshow(cpu_per_core_usage.T, aspect='auto', cmap='Greys', extent=[timestamps[0], timestamps[-1], 0, cpu_per_core_usage.shape[1]])
    plt.colorbar(label='CPU Usage (%)')
    plt.xlabel('Time (seconds)')
    plt.ylabel('CPU Core Index')
    plt.title(f'CPU Usage Heatmap - {"Processes" if args.processes else "Threads"}')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.show()
