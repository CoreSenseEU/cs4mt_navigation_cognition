#!/usr/bin/env python3
"""
Navigation Metrics Analysis Tool

Analyzes navigation data to extract:
- Minimum distance to goal
- Average near-goal distance  
- Time to complete navigation
- Time to reach goal threshold

Usage:
  python3 plot_nav_metrics.py <npz_file>           # Single file
  python3 plot_nav_metrics.py --dir <directory>    # All files in directory
  python3 plot_nav_metrics.py --list <directory>   # List available files
  python3 plot_nav_metrics.py --compare <f1> <f2>  # Compare two runs
"""

import numpy as np
import sys
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime


def extract_nav_metrics(npz_file, goal_threshold=0.1):
    """
    Extract navigation metrics from a single NPZ file.
    
    Args:
        npz_file: Path to NPZ file with 'time', 'distance', 'inflation_radius'
        goal_threshold: Distance threshold to consider goal reached (meters)
    
    Returns:
        dict with all metrics
    """
    data = np.load(npz_file)
    time = data['time']
    distance = data['distance']
    inflation_radius = data['inflation_radius']
    
    # Basic metrics
    min_distance = np.min(distance)
    min_distance_idx = np.argmin(distance)
    min_distance_time = time[min_distance_idx]
    total_time = time[-1] - time[0]
    
    # Average distance when near goal (within 20% of minimum)
    near_goal_threshold = min_distance * 1.2
    near_goal_mask = distance <= near_goal_threshold
    avg_min_distance = np.mean(distance[near_goal_mask])
    std_min_distance = np.std(distance[near_goal_mask])
    samples_near_goal = np.sum(near_goal_mask)
    
    # Time to reach goal threshold
    reached_goal_mask = distance <= goal_threshold
    if np.any(reached_goal_mask):
        time_to_goal = time[np.argmax(reached_goal_mask)] - time[0]
        goal_reached = True
    else:
        time_to_goal = None
        goal_reached = False
    
    # Settling time (time spent near goal)
    if goal_reached:
        settling_time = total_time - time_to_goal
    else:
        settling_time = None
    
    # Inflation radius metrics
    ir_initial = inflation_radius[0]
    ir_final = inflation_radius[-1]
    ir_min = np.min(inflation_radius)
    ir_max = np.max(inflation_radius)
    
    return {
        'file': npz_file,
        'filename': os.path.basename(npz_file),
        'n_samples': len(time),
        'total_time': total_time,
        'min_distance': min_distance,
        'min_distance_mm': min_distance * 1000,
        'min_distance_time': min_distance_time,
        'avg_min_distance': avg_min_distance,
        'avg_min_distance_mm': avg_min_distance * 1000,
        'std_min_distance': std_min_distance,
        'samples_near_goal': samples_near_goal,
        'goal_threshold': goal_threshold,
        'goal_reached': goal_reached,
        'time_to_goal': time_to_goal,
        'settling_time': settling_time,
        'ir_initial': ir_initial,
        'ir_final': ir_final,
        'ir_min': ir_min,
        'ir_max': ir_max,
        # Raw data for plotting
        'time': time,
        'distance': distance,
        'inflation_radius': inflation_radius,
    }


def print_metrics(metrics):
    """Print metrics in a formatted way"""
    print(f"\n{'='*60}")
    print(f"NAVIGATION METRICS: {metrics['filename']}")
    print(f"{'='*60}")
    
    print(f"\n--- Distance to Goal ---")
    print(f"  Minimum distance:     {metrics['min_distance']:.4f} m ({metrics['min_distance_mm']:.1f} mm)")
    print(f"  Time at minimum:      {metrics['min_distance_time']:.2f} s")
    print(f"  Avg near-goal dist:   {metrics['avg_min_distance']:.4f} m ({metrics['avg_min_distance_mm']:.1f} mm)")
    print(f"  Std near-goal:        {metrics['std_min_distance']:.4f} m")
    print(f"  Samples near goal:    {metrics['samples_near_goal']}")
    
    print(f"\n--- Timing ---")
    print(f"  Total duration:       {metrics['total_time']:.2f} s")
    if metrics['goal_reached']:
        print(f"  Time to goal (<{metrics['goal_threshold']}m): {metrics['time_to_goal']:.2f} s")
        print(f"  Settling time:        {metrics['settling_time']:.2f} s")
    else:
        print(f"  Time to goal (<{metrics['goal_threshold']}m): NOT REACHED")
    
    print(f"\n--- Inflation Radius ---")
    print(f"  Initial: {metrics['ir_initial']:.3f} m")
    print(f"  Final:   {metrics['ir_final']:.3f} m")
    print(f"  Min:     {metrics['ir_min']:.3f} m")
    print(f"  Max:     {metrics['ir_max']:.3f} m")


def plot_single_run(metrics, output_file=None):
    """
    Plot navigation metrics for a single run.
    
    Creates a 2x2 figure with:
    - Distance vs Time
    - Inflation Radius vs Time
    - Distance histogram (near goal)
    - Summary metrics text
    """
    if output_file is None:
        output_file = metrics['file'].replace('.npz', '_metrics.png')
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    time = metrics['time']
    distance = metrics['distance']
    inflation_radius = metrics['inflation_radius']
    
    # --- Plot 1: Distance vs Time ---
    ax = axes[0, 0]
    ax.plot(time, distance, 'b-', linewidth=1.5, label='Distance to Goal')
    ax.axhline(y=metrics['min_distance'], color='g', linestyle='--', alpha=0.7, 
               label=f"Min: {metrics['min_distance_mm']:.1f} mm")
    ax.axhline(y=metrics['goal_threshold'], color='orange', linestyle=':', alpha=0.7,
               label=f"Goal threshold: {metrics['goal_threshold']} m")
    ax.scatter([metrics['min_distance_time']], [metrics['min_distance']], 
               color='r', s=100, zorder=5, marker='v', label=f"Min @ {metrics['min_distance_time']:.1f}s")
    if metrics['time_to_goal'] is not None:
        ax.axvline(x=metrics['time_to_goal'], color='green', linestyle='-', alpha=0.5,
                   label=f"Goal reached @ {metrics['time_to_goal']:.1f}s")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance (m)')
    ax.set_title('Distance to Goal Over Time')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # --- Plot 2: Inflation Radius vs Time ---
    ax = axes[0, 1]
    ax.plot(time, inflation_radius, 'r-', linewidth=1.5)
    ax.axhline(y=metrics['ir_min'], color='orange', linestyle='--', alpha=0.7,
               label=f"Min: {metrics['ir_min']:.3f} m")
    ax.axhline(y=metrics['ir_max'], color='purple', linestyle='--', alpha=0.7,
               label=f"Max: {metrics['ir_max']:.3f} m")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Inflation Radius (m)')
    ax.set_title('Inflation Radius Over Time')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # --- Plot 3: Distance + Inflation on same plot (dual axis) ---
    ax = axes[1, 0]
    ax2 = ax.twinx()
    
    l1, = ax.plot(time, distance, 'b-', linewidth=1.5, label='Distance')
    l2, = ax2.plot(time, inflation_radius, 'r-', linewidth=1.5, alpha=0.7, label='Inflation Radius')
    
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance (m)', color='b')
    ax2.set_ylabel('Inflation Radius (m)', color='r')
    ax.tick_params(axis='y', labelcolor='b')
    ax2.tick_params(axis='y', labelcolor='r')
    ax.set_title('Distance & Inflation Radius (Combined)')
    ax.legend(handles=[l1, l2], loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # --- Plot 4: Summary Text ---
    ax = axes[1, 1]
    ax.axis('off')
    
    summary_text = f"""
    FILE: {metrics['filename']}
    
    ━━━ DISTANCE METRICS ━━━
    Minimum Distance:      {metrics['min_distance_mm']:.1f} mm
    Avg Near-Goal:         {metrics['avg_min_distance_mm']:.1f} mm
    Std Near-Goal:         {metrics['std_min_distance']*1000:.1f} mm
    
    ━━━ TIMING METRICS ━━━
    Total Duration:        {metrics['total_time']:.2f} s
    Time to Goal:          {metrics['time_to_goal']:.2f} s if metrics['time_to_goal'] else 'N/A'
    Settling Time:         {metrics['settling_time']:.2f} s if metrics['settling_time'] else 'N/A'
    
    ━━━ INFLATION RADIUS ━━━
    Range: {metrics['ir_min']:.3f} - {metrics['ir_max']:.3f} m
    Initial → Final: {metrics['ir_initial']:.3f} → {metrics['ir_final']:.3f} m
    
    ━━━ DATA ━━━
    Samples: {metrics['n_samples']}
    """
    
    # Fix the conditional formatting
    if metrics['time_to_goal'] is not None:
        ttg = f"{metrics['time_to_goal']:.2f} s"
    else:
        ttg = "NOT REACHED"
    
    if metrics['settling_time'] is not None:
        st = f"{metrics['settling_time']:.2f} s"
    else:
        st = "N/A"
    
    summary_text = f"""
FILE: {metrics['filename']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         DISTANCE METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Minimum Distance:      {metrics['min_distance_mm']:.1f} mm
  Avg Near-Goal:         {metrics['avg_min_distance_mm']:.1f} mm
  Std Near-Goal:         {metrics['std_min_distance']*1000:.1f} mm

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           TIMING METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Duration:        {metrics['total_time']:.2f} s
  Time to Goal:          {ttg}
  Settling Time:         {st}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
         INFLATION RADIUS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Range: {metrics['ir_min']:.3f} - {metrics['ir_max']:.3f} m
  Initial → Final: {metrics['ir_initial']:.3f} → {metrics['ir_final']:.3f} m

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Samples: {metrics['n_samples']}
"""
    
    ax.text(0.1, 0.95, summary_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPlot saved to: {output_file}")
    
    return output_file


def plot_multiple_runs(metrics_list, output_file='nav_comparison.png'):
    """
    Plot comparison of multiple navigation runs.
    Args:
        metrics_list: List of metrics dicts from extract_nav_metrics()
        output_file: Output image path
    """
    n_runs = len(metrics_list)
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))

    # Collect aggregate data
    min_distances = [m['min_distance_mm'] for m in metrics_list]
    avg_distances = [m['avg_min_distance_mm'] for m in metrics_list]
    total_times = [m['total_time'] for m in metrics_list]
    times_to_goal = [m['time_to_goal'] for m in metrics_list if m['time_to_goal'] is not None]
    labels = [m['filename'][:20] for m in metrics_list]

    # --- Plot 1: Min Distance Bar Chart ---
    ax = axes[0, 0]
    x = np.arange(n_runs)
    ax.bar(x, min_distances, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axhline(y=np.mean(min_distances), color='r', linestyle='--', label=f"Mean: {np.mean(min_distances):.1f} mm")
    ax.set_xlabel('Run')
    ax.set_ylabel('Min Distance (mm)')
    ax.set_title('Minimum Distance to Goal')
    ax.set_xticks(x)
    ax.set_xticklabels([f'R{i+1}' for i in range(n_runs)], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # --- Plot 2: Time to Complete Bar Chart ---
    ax = axes[0, 1]
    ax.bar(x, total_times, color='coral', alpha=0.7, edgecolor='black')
    ax.axhline(y=np.mean(total_times), color='r', linestyle='--', label=f"Mean: {np.mean(total_times):.1f} s")
    ax.set_xlabel('Run')
    ax.set_ylabel('Total Time (s)')
    ax.set_title('Total Navigation Time')
    ax.set_xticks(x)
    ax.set_xticklabels([f'R{i+1}' for i in range(n_runs)], rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    # --- Plot 3: Distance Histogram ---
    ax = axes[0, 2]
    ax.hist(min_distances, bins='auto', color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(x=np.mean(min_distances), color='r', linestyle='--', linewidth=2, label=f"Mean: {np.mean(min_distances):.1f} mm")
    ax.axvline(x=np.median(min_distances), color='g', linestyle=':', linewidth=2, label=f"Median: {np.median(min_distances):.1f} mm")
    ax.set_xlabel('Min Distance (mm)')
    ax.set_ylabel('Count')
    ax.set_title('Min Distance Distribution')
    ax.legend()

    # --- Plot 4: All Distance Traces ---
    ax = axes[1, 0]
    for i, m in enumerate(metrics_list):
        ax.plot(m['time'], m['distance'], alpha=0.6, linewidth=1, label=f"R{i+1}")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance (m)')
    ax.set_title('Distance Traces (All Runs)')
    if n_runs <= 10:
        ax.legend(loc='upper right', fontsize=7)
    ax.grid(True, alpha=0.3)

    # --- Plot 5: All Inflation Radius Traces ---
    ax = axes[1, 1]
    for i, m in enumerate(metrics_list):
        ax.plot(m['time'], m['inflation_radius'], alpha=0.6, linewidth=1, label=f"R{i+1}")
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Inflation Radius (m)')
    ax.set_title('Inflation Radius Traces (All Runs)')
    if n_runs <= 10:
        ax.legend(loc='upper right', fontsize=7)
    ax.grid(True, alpha=0.3)

    # --- Plot 6: Summary Statistics ---
    ax = axes[1, 2]
    ax.axis('off')

    # Pre-compute conditionals BEFORE the f-string
    ttg_mean = f"{np.mean(times_to_goal):.2f}" if times_to_goal else 'N/A'
    ttg_std  = f"{np.std(times_to_goal, ddof=1):.2f}" if len(times_to_goal) > 1 else 'N/A'

    stats_text = f"""
AGGREGATE STATISTICS ({n_runs} runs)

MINIMUM DISTANCE (mm):
  Mean:   {np.mean(min_distances):.1f}
  Std:    {np.std(min_distances, ddof=1):.1f}
  Min:    {np.min(min_distances):.1f}
  Max:    {np.max(min_distances):.1f}

AVG NEAR-GOAL DISTANCE (mm):
  Mean:   {np.mean(avg_distances):.1f}
  Std:    {np.std(avg_distances, ddof=1):.1f}

TOTAL TIME (s):
  Mean:   {np.mean(total_times):.2f}
  Std:    {np.std(total_times, ddof=1):.2f}
  Min:    {np.min(total_times):.2f}
  Max:    {np.max(total_times):.2f}

TIME TO GOAL (s): ({len(times_to_goal)}/{n_runs} reached)
  Mean:   {ttg_mean}
  Std:    {ttg_std}
"""

    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nComparison plot saved to: {output_file}")

    return output_file


def list_npz_files(directory):
    """List all NPZ files in a directory with basic info"""
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
    
    files = sorted(glob.glob(os.path.join(directory, '*.npz')))
    
    print(f"\n{'='*70}")
    print(f"NPZ FILES IN: {directory}")
    print(f"{'='*70}")
    
    nav_files = []
    aruco_files = []
    other_files = []
    
    for f in files:
        try:
            data = np.load(f)
            keys = list(data.files)
            
            # Categorize
            if 'time' in keys and 'distance' in keys and 'inflation_radius' in keys:
                nav_files.append(f)
                category = "NAV"
            elif 'distances' in keys or 'positions' in keys:
                aruco_files.append(f)
                category = "ARUCO"
            else:
                other_files.append(f)
                category = "OTHER"
            
            # Get file info
            size = os.path.getsize(f) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d %H:%M')
            
            print(f"[{category:5}] {os.path.basename(f):40} {size:6.1f} KB  {mtime}  keys={keys[:3]}...")
            
        except Exception as e:
            print(f"[ERROR] {os.path.basename(f):40} - {e}")
    
    print(f"\n--- Summary ---")
    print(f"  Navigation files: {len(nav_files)}")
    print(f"  ArUco files:      {len(aruco_files)}")
    print(f"  Other files:      {len(other_files)}")
    
    return {
        'nav': nav_files,
        'aruco': aruco_files,
        'other': other_files,
        'all': files
    }


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nQuick start:")
        print("  python3 plot_nav_metrics.py --list ~/navigation_data")
        sys.exit(0)
    
    arg = sys.argv[1]
    
    if arg == '--list':
        # List files in directory
        directory = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/navigation_data')
        list_npz_files(directory)
    
    elif arg == '--dir':
        # Analyze all nav files in directory
        directory = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser('~/navigation_data')
        file_info = list_npz_files(directory)
        
        if file_info['nav']:
            print(f"\nAnalyzing {len(file_info['nav'])} navigation files...")
            metrics_list = []
            for f in file_info['nav']:
                try:
                    m = extract_nav_metrics(f)
                    print_metrics(m)
                    metrics_list.append(m)
                except Exception as e:
                    print(f"Error processing {f}: {e}")
            
            if len(metrics_list) > 1:
                plot_multiple_runs(metrics_list)
        else:
            print("No navigation files found (need 'time', 'distance', 'inflation_radius' keys)")
    
    elif arg == '--compare':
        # Compare specific files
        if len(sys.argv) < 4:
            print("Usage: --compare <file1.npz> <file2.npz> [file3.npz ...]")
            sys.exit(1)
        
        files = sys.argv[2:]
        metrics_list = []
        for f in files:
            if os.path.isfile(f):
                m = extract_nav_metrics(f)
                print_metrics(m)
                metrics_list.append(m)
            else:
                print(f"File not found: {f}")
        
        if len(metrics_list) > 1:
            plot_multiple_runs(metrics_list)
    
    elif os.path.isfile(arg):
        # Single file analysis
        metrics = extract_nav_metrics(arg)
        print_metrics(metrics)
        plot_single_run(metrics)
    
    else:
        print(f"Not found: {arg}")
        print("Use --list <directory> to see available files")


if __name__ == '__main__':
    main()