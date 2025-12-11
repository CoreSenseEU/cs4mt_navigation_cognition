#!/usr/bin/env python3
import numpy as np
import sys
import os
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def print_npz_keys(npz_file):
    """Print all keys in the NPZ file"""
    data = np.load(npz_file)
    print(f"\nKeys in {os.path.basename(npz_file)}:")
    for key in data.files:
        arr = data[key]
        if isinstance(arr, np.ndarray):
            print(f"  {key}: shape={arr.shape}, dtype={arr.dtype}")
        else:
            print(f"  {key}: {arr}")


def print_aruco_data(npz_file):
    """Print ArUco recording data from NPZ file"""
    data = np.load(npz_file)
    
    print(f"\n=== ArUco Recording Data ===")
    print(f"File: {os.path.basename(npz_file)}")
    print(f"Available keys: {data.files}")
    
    if 'distances' in data.files:
        distances = data['distances']
        print(f"\n--- ArUco Distances ---")
        print(f"  Samples: {len(distances)}")
        print(f"  Mean: {np.mean(distances):.4f} m")
        print(f"  Std: {np.std(distances):.4f} m")
        print(f"  Min: {np.min(distances):.4f} m")
        print(f"  Max: {np.max(distances):.4f} m")
    
    if 'positions' in data.files:
        positions = data['positions']
        print(f"\n--- Marker Positions ---")
        print(f"  Shape: {positions.shape}")
        print(f"  X: mean={np.mean(positions[:,0]):.4f}, std={np.std(positions[:,0]):.4f}")
        print(f"  Y: mean={np.mean(positions[:,1]):.4f}, std={np.std(positions[:,1]):.4f}")
        print(f"  Z: mean={np.mean(positions[:,2]):.4f}, std={np.std(positions[:,2]):.4f}")
    
    if 'marker_ids' in data.files:
        marker_ids = data['marker_ids']
        unique_ids = np.unique(marker_ids)
        print(f"\n--- Marker IDs ---")
        print(f"  Unique IDs: {unique_ids}")
        for mid in unique_ids:
            count = np.sum(marker_ids == mid)
            print(f"  ID {mid}: {count} samples")
    
    if 'tf_poses' in data.files:
        tf_poses = data['tf_poses']
        valid = ~np.isnan(tf_poses).any(axis=1)
        print(f"\n--- TF Poses (x, y, yaw) ---")
        print(f"  Total: {len(tf_poses)}, Valid: {np.sum(valid)}")
        if np.sum(valid) > 0:
            print(f"  X: mean={np.nanmean(tf_poses[:,0]):.4f}, std={np.nanstd(tf_poses[:,0]):.4f}")
            print(f"  Y: mean={np.nanmean(tf_poses[:,1]):.4f}, std={np.nanstd(tf_poses[:,1]):.4f}")
            print(f"  Yaw: mean={np.nanmean(tf_poses[:,2]):.4f}, std={np.nanstd(tf_poses[:,2]):.4f}")
    
    if 'amcl_positions' in data.files:
        amcl_pos = data['amcl_positions']
        valid = ~np.isnan(amcl_pos).any(axis=1)
        print(f"\n--- AMCL Positions (x, y, z) ---")
        print(f"  Total: {len(amcl_pos)}, Valid: {np.sum(valid)}")
        if np.sum(valid) > 0:
            print(f"  X: mean={np.nanmean(amcl_pos[:,0]):.4f}, std={np.nanstd(amcl_pos[:,0]):.4f}")
            print(f"  Y: mean={np.nanmean(amcl_pos[:,1]):.4f}, std={np.nanstd(amcl_pos[:,1]):.4f}")
            print(f"  Z: mean={np.nanmean(amcl_pos[:,2]):.4f}, std={np.nanstd(amcl_pos[:,2]):.4f}")
    
    if 'amcl_orientations' in data.files:
        amcl_ori = data['amcl_orientations']
        valid = ~np.isnan(amcl_ori).any(axis=1)
        print(f"\n--- AMCL Orientations (qx, qy, qz, qw) ---")
        print(f"  Total: {len(amcl_ori)}, Valid: {np.sum(valid)}")
    
    if 'recording_duration' in data.files:
        print(f"\n--- Recording Info ---")
        print(f"  Duration: {data['recording_duration']} s")
    if 'num_samples' in data.files:
        print(f"  Num samples: {data['num_samples']}")


def analyze_positional_error(files):
    """Analyze positional error across recordings"""
    
    print(f"\n{'='*60}")
    print("POSITIONAL ERROR ANALYSIS")
    print(f"{'='*60}")
    
    # Collect final position from each recording
    final_positions = []
    
    for f in files:
        data = np.load(f)
        if 'positions' in data.files:
            positions = data['positions']
            if len(positions) > 0:
                # Use mean position of this recording
                final_positions.append([
                    np.mean(positions[:, 0]),
                    np.mean(positions[:, 1]),
                    np.mean(positions[:, 2])
                ])
    
    if len(final_positions) < 2:
        print("Not enough recordings for error analysis")
        return None
    
    final_positions = np.array(final_positions)
    n = len(final_positions)
    
    # Reference positions
    mean_pos = np.mean(final_positions, axis=0)
    first_pos = final_positions[0]
    
    print(f"\nN recordings: {n}")
    print(f"\nReference Positions:")
    print(f"  Mean:  X={mean_pos[0]:.4f}, Y={mean_pos[1]:.4f}, Z={mean_pos[2]:.4f}")
    print(f"  First: X={first_pos[0]:.4f}, Y={first_pos[1]:.4f}, Z={first_pos[2]:.4f}")
    
    # --- ERROR FROM MEAN (Repeatability/Precision) ---
    print(f"\n--- Error from MEAN (Repeatability) ---")
    
    errors_from_mean_3d = np.linalg.norm(final_positions - mean_pos, axis=1)
    errors_from_mean_2d = np.linalg.norm(final_positions[:, :2] - mean_pos[:2], axis=1)
    
    print(f"\n3D Error:")
    print(f"  Mean:   {np.mean(errors_from_mean_3d):.4f} m")
    print(f"  Std:    {np.std(errors_from_mean_3d, ddof=1):.4f} m")
    print(f"  Max:    {np.max(errors_from_mean_3d):.4f} m")
    print(f"  Min:    {np.min(errors_from_mean_3d):.4f} m")
    
    print(f"\n2D Error (X-Y plane):")
    print(f"  Mean:   {np.mean(errors_from_mean_2d):.4f} m")
    print(f"  Std:    {np.std(errors_from_mean_2d, ddof=1):.4f} m")
    print(f"  Max:    {np.max(errors_from_mean_2d):.4f} m")
    print(f"  Min:    {np.min(errors_from_mean_2d):.4f} m")
    
    # --- ERROR FROM FIRST (Drift) ---
    print(f"\n--- Error from FIRST recording (Drift) ---")
    
    errors_from_first_3d = np.linalg.norm(final_positions - first_pos, axis=1)
    errors_from_first_2d = np.linalg.norm(final_positions[:, :2] - first_pos[:2], axis=1)
    
    print(f"\n3D Error:")
    print(f"  Mean:   {np.mean(errors_from_first_3d):.4f} m")
    print(f"  Std:    {np.std(errors_from_first_3d, ddof=1):.4f} m")
    print(f"  Max:    {np.max(errors_from_first_3d):.4f} m")
    print(f"  Min:    {np.min(errors_from_first_3d):.4f} m")
    
    print(f"\n2D Error (X-Y plane):")
    print(f"  Mean:   {np.mean(errors_from_first_2d):.4f} m")
    print(f"  Std:    {np.std(errors_from_first_2d, ddof=1):.4f} m")
    print(f"  Max:    {np.max(errors_from_first_2d):.4f} m")
    print(f"  Min:    {np.min(errors_from_first_2d):.4f} m")
    
    # --- PER-AXIS ERROR ---
    print(f"\n--- Per-Axis Error (from mean) ---")
    for i, axis in enumerate(['X', 'Y', 'Z']):
        axis_errors = np.abs(final_positions[:, i] - mean_pos[i])
        print(f"  {axis}: Mean={np.mean(axis_errors):.4f} m, Max={np.max(axis_errors):.4f} m")
    
    return {
        'final_positions': final_positions,
        'mean_pos': mean_pos,
        'first_pos': first_pos,
        'errors_from_mean_2d': errors_from_mean_2d,
        'errors_from_mean_3d': errors_from_mean_3d,
        'errors_from_first_2d': errors_from_first_2d,
        'errors_from_first_3d': errors_from_first_3d,
    }


def plot_positional_error(error_data, output_file='positional_error.png'):
    """Plot positional error analysis"""
    
    if error_data is None:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    final_positions = error_data['final_positions']
    mean_pos = error_data['mean_pos']
    first_pos = error_data['first_pos']
    
    # Scatter plot of all positions
    ax = axes[0, 0]
    ax.scatter(final_positions[:, 0], final_positions[:, 1], alpha=0.7, label='Recordings')
    ax.scatter(mean_pos[0], mean_pos[1], color='r', s=150, marker='x', linewidths=3, label='Mean')
    ax.scatter(first_pos[0], first_pos[1], color='g', s=150, marker='+', linewidths=3, label='First')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('Position Scatter (X-Y)')
    ax.legend()
    ax.axis('equal')
    ax.grid(True, alpha=0.3)
    
    # Error from mean histogram
    ax = axes[0, 1]
    ax.hist(error_data['errors_from_mean_2d'] * 1000, bins='auto', edgecolor='black', alpha=0.7)
    ax.axvline(np.mean(error_data['errors_from_mean_2d']) * 1000, color='r', linestyle='--', label='Mean')
    ax.set_xlabel('2D Error from Mean (mm)')
    ax.set_ylabel('Count')
    ax.set_title('Error from Mean (Repeatability)')
    ax.legend()
    
    # Error from first histogram
    ax = axes[1, 0]
    ax.hist(error_data['errors_from_first_2d'] * 1000, bins='auto', edgecolor='black', alpha=0.7, color='orange')
    ax.axvline(np.mean(error_data['errors_from_first_2d']) * 1000, color='r', linestyle='--', label='Mean')
    ax.set_xlabel('2D Error from First (mm)')
    ax.set_ylabel('Count')
    ax.set_title('Error from First Recording (Drift)')
    ax.legend()
    
    # Error over time (recording index)
    ax = axes[1, 1]
    indices = np.arange(len(final_positions))
    ax.plot(indices, error_data['errors_from_mean_2d'] * 1000, 'b-o', label='From Mean')
    ax.plot(indices, error_data['errors_from_first_2d'] * 1000, 'r-s', label='From First')
    ax.set_xlabel('Recording Index')
    ax.set_ylabel('2D Error (mm)')
    ax.set_title('Error Over Time')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nPositional error plot saved to {output_file}")


def analyze_multiple_recordings(files):
    """Statistical analysis across multiple recordings"""
    
    print(f"\n{'='*60}")
    print(f"STATISTICAL ANALYSIS ACROSS {len(files)} RECORDINGS")
    print(f"{'='*60}")
    
    # Collect per-recording means
    recording_means = {
        'distance': [],
        'pos_x': [],
        'pos_y': [],
        'pos_z': [],
        'amcl_x': [],
        'amcl_y': [],
        'tf_x': [],
        'tf_y': [],
        'tf_yaw': [],
    }
    
    for f in files:
        data = np.load(f)
        
        if 'distances' in data.files:
            distances = data['distances']
            if len(distances) > 0:
                recording_means['distance'].append(np.mean(distances))
        
        if 'positions' in data.files:
            positions = data['positions']
            if len(positions) > 0:
                recording_means['pos_x'].append(np.mean(positions[:, 0]))
                recording_means['pos_y'].append(np.mean(positions[:, 1]))
                recording_means['pos_z'].append(np.mean(positions[:, 2]))
        
        if 'amcl_positions' in data.files:
            amcl_pos = data['amcl_positions']
            valid = ~np.isnan(amcl_pos).any(axis=1)
            if np.sum(valid) > 0:
                recording_means['amcl_x'].append(np.nanmean(amcl_pos[:, 0]))
                recording_means['amcl_y'].append(np.nanmean(amcl_pos[:, 1]))
        
        if 'tf_poses' in data.files:
            tf_poses = data['tf_poses']
            valid = ~np.isnan(tf_poses).any(axis=1)
            if np.sum(valid) > 0:
                recording_means['tf_x'].append(np.nanmean(tf_poses[:, 0]))
                recording_means['tf_y'].append(np.nanmean(tf_poses[:, 1]))
                recording_means['tf_yaw'].append(np.nanmean(tf_poses[:, 2]))
    
    # Print statistics
    def print_stats(name, values):
        if len(values) == 0:
            return
        values = np.array(values)
        n = len(values)
        mean = np.mean(values)
        std = np.std(values, ddof=1)  # Sample std
        stderr = std / np.sqrt(n)
        ci_95 = 1.96 * stderr
        
        print(f"\n{name}:")
        print(f"  N recordings: {n}")
        print(f"  Mean: {mean:.4f}")
        print(f"  Std Dev: {std:.4f}")
        print(f"  Std Error: {stderr:.4f}")
        print(f"  95% CI: {mean:.4f} ± {ci_95:.4f} [{mean-ci_95:.4f}, {mean+ci_95:.4f}]")
    
    print_stats("ArUco Distance (m)", recording_means['distance'])
    print_stats("Marker Position X (m)", recording_means['pos_x'])
    print_stats("Marker Position Y (m)", recording_means['pos_y'])
    print_stats("Marker Position Z (m)", recording_means['pos_z'])
    print_stats("AMCL Position X (m)", recording_means['amcl_x'])
    print_stats("AMCL Position Y (m)", recording_means['amcl_y'])
    print_stats("TF Pose X (m)", recording_means['tf_x'])
    print_stats("TF Pose Y (m)", recording_means['tf_y'])
    print_stats("TF Pose Yaw (rad)", recording_means['tf_yaw'])
    
    # Statistical significance assessment
    print(f"\n{'='*60}")
    print("STATISTICAL SIGNIFICANCE ASSESSMENT")
    print(f"{'='*60}")
    
    n = len(files)
    if n >= 20:
        print(f"✓ {n} recordings is generally acceptable for robotics experiments")
    elif n >= 10:
        print(f"⚠ {n} recordings is marginal - consider more runs for high-variance data")
    else:
        print(f"✗ {n} recordings is likely insufficient for statistical significance")
    
    # Check coefficient of variation for key metrics
    if len(recording_means['distance']) > 1:
        cv = np.std(recording_means['distance']) / np.mean(recording_means['distance']) * 100
        print(f"\nDistance Coefficient of Variation: {cv:.1f}%")
        if cv < 10:
            print("  ✓ Low variance - results are consistent")
        elif cv < 25:
            print("  ⚠ Moderate variance - consider more runs")
        else:
            print("  ✗ High variance - need more runs for confidence")
    
    return recording_means


def plot_statistical_summary(recording_means, output_file='statistical_summary.png'):
    """Plot statistical summary across recordings"""
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Distance histogram
    if len(recording_means['distance']) > 0:
        ax = axes[0, 0]
        ax.hist(recording_means['distance'], bins='auto', edgecolor='black', alpha=0.7)
        ax.axvline(np.mean(recording_means['distance']), color='r', linestyle='--', label='Mean')
        ax.set_xlabel('Distance (m)')
        ax.set_ylabel('Count')
        ax.set_title('ArUco Distance Distribution Across Recordings')
        ax.legend()
    
    # Position scatter
    if len(recording_means['pos_x']) > 0:
        ax = axes[0, 1]
        ax.scatter(recording_means['pos_x'], recording_means['pos_y'], alpha=0.7)
        ax.scatter(np.mean(recording_means['pos_x']), np.mean(recording_means['pos_y']), 
                   color='r', s=100, marker='x', label='Mean')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Marker Position (per recording mean)')
        ax.legend()
        ax.axis('equal')
    
    # AMCL position scatter
    if len(recording_means['amcl_x']) > 0:
        ax = axes[1, 0]
        ax.scatter(recording_means['amcl_x'], recording_means['amcl_y'], alpha=0.7)
        ax.scatter(np.mean(recording_means['amcl_x']), np.mean(recording_means['amcl_y']),
                   color='r', s=100, marker='x', label='Mean')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('AMCL Position (per recording mean)')
        ax.legend()
        ax.axis('equal')
    
    # Error bars summary
    ax = axes[1, 1]
    metrics = []
    means = []
    errors = []
    
    for name, key in [('Distance', 'distance'), ('Pos X', 'pos_x'), ('Pos Y', 'pos_y'), 
                       ('AMCL X', 'amcl_x'), ('AMCL Y', 'amcl_y')]:
        if len(recording_means[key]) > 1:
            metrics.append(name)
            means.append(np.mean(recording_means[key]))
            errors.append(np.std(recording_means[key]) / np.sqrt(len(recording_means[key])))
    
    if metrics:
        ax.barh(metrics, means, xerr=errors, capsize=5, alpha=0.7)
        ax.set_xlabel('Value (m)')
        ax.set_title('Mean ± Standard Error')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nStatistical summary plot saved to {output_file}")


def find_aruco_recordings(data_dir=None):
    """Find all aruco recording files"""
    if data_dir is None:
        data_dir = os.path.expanduser('~/navigation_data')
    
    patterns = [
        os.path.join(data_dir, 'aruco_recording_*.npz'),
        os.path.join(data_dir, 'aruco_recordings', 'aruco_recording_*.npz')
    ]
    
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    
    return sorted(files)


def plot_navigation_data(npz_file):
    """Load and plot navigation data from NPZ file"""
    data = np.load(npz_file)
    time = data['time']
    distance = data['distance']
    inflation_radius = data['inflation_radius']
    
    print(f"Loaded {len(time)} data points from {npz_file}")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    ax1.plot(time, distance, 'b-', linewidth=2, label='Distance to Goal')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Distance (m)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f'Navigation Data - {os.path.basename(npz_file)}')
    
    ax2.plot(time, inflation_radius, 'r-', linewidth=2, label='Inflation Radius')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Radius (m)', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    output_image = npz_file.replace('.npz', '.png')
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_image}")


def main():
    data_dir = os.path.expanduser('~/navigation_data')
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 plot_navigation_data.py <npz_file>")
        print("  python3 plot_navigation_data.py --list      # List all aruco recordings")
        print("  python3 plot_navigation_data.py --latest    # Print latest aruco recording")
        print("  python3 plot_navigation_data.py --all       # Print all aruco recordings")
        print("  python3 plot_navigation_data.py --stats     # Statistical analysis across all recordings")
        print("  python3 plot_navigation_data.py --error     # Positional error analysis")
        sys.exit(0)
    
    arg = sys.argv[1]
    
    if arg == '--list':
        files = find_aruco_recordings(data_dir)
        print(f"\nFound {len(files)} ArUco recordings:")
        for f in files:
            print(f"  {f}")
    
    elif arg == '--latest':
        files = find_aruco_recordings(data_dir)
        if files:
            print_aruco_data(files[-1])
        else:
            print("No ArUco recordings found")
    
    elif arg == '--all':
        files = find_aruco_recordings(data_dir)
        if files:
            for f in files:
                print_aruco_data(f)
                print("\n" + "="*60)
        else:
            print("No ArUco recordings found")
    
    elif arg == '--stats':
        files = find_aruco_recordings(data_dir)
        if files:
            recording_means = analyze_multiple_recordings(files)
            plot_statistical_summary(recording_means)
        else:
            print("No ArUco recordings found")
    
    elif arg == '--error':
        files = find_aruco_recordings(data_dir)
        if files:
            error_data = analyze_positional_error(files)
            plot_positional_error(error_data)
        else:
            print("No ArUco recordings found")
    
    elif os.path.isfile(arg):
        if 'aruco_recording' in arg:
            print_aruco_data(arg)
        else:
            plot_navigation_data(arg)
    
    else:
        print(f"File not found: {arg}")


if __name__ == '__main__':
    main()