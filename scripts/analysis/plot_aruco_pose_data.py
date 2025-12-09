#!/usr/bin/env python3
import numpy as np
import sys
import os
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
    
    # Check available keys
    print(f"\nAvailable keys: {data.files}")
    
    # Distances
    if 'distances' in data.files:
        distances = data['distances']
        print(f"\n--- ArUco Distances ---")
        print(f"  Samples: {len(distances)}")
        print(f"  Mean: {np.mean(distances):.4f} m")
        print(f"  Std: {np.std(distances):.4f} m")
        print(f"  Min: {np.min(distances):.4f} m")
        print(f"  Max: {np.max(distances):.4f} m")
    
    # Marker positions
    if 'positions' in data.files:
        positions = data['positions']
        print(f"\n--- Marker Positions ---")
        print(f"  Shape: {positions.shape}")
        print(f"  X: mean={np.mean(positions[:,0]):.4f}, std={np.std(positions[:,0]):.4f}")
        print(f"  Y: mean={np.mean(positions[:,1]):.4f}, std={np.std(positions[:,1]):.4f}")
        print(f"  Z: mean={np.mean(positions[:,2]):.4f}, std={np.std(positions[:,2]):.4f}")
    
    # Marker IDs
    if 'marker_ids' in data.files:
        marker_ids = data['marker_ids']
        unique_ids = np.unique(marker_ids)
        print(f"\n--- Marker IDs ---")
        print(f"  Unique IDs: {unique_ids}")
        for mid in unique_ids:
            count = np.sum(marker_ids == mid)
            print(f"  ID {mid}: {count} samples")
    
    # TF poses
    if 'tf_poses' in data.files:
        tf_poses = data['tf_poses']
        valid = ~np.isnan(tf_poses).any(axis=1)
        print(f"\n--- TF Poses (x, y, yaw) ---")
        print(f"  Total: {len(tf_poses)}, Valid: {np.sum(valid)}")
        if np.sum(valid) > 0:
            print(f"  X: mean={np.nanmean(tf_poses[:,0]):.4f}, std={np.nanstd(tf_poses[:,0]):.4f}")
            print(f"  Y: mean={np.nanmean(tf_poses[:,1]):.4f}, std={np.nanstd(tf_poses[:,1]):.4f}")
            print(f"  Yaw: mean={np.nanmean(tf_poses[:,2]):.4f}, std={np.nanstd(tf_poses[:,2]):.4f}")
    
    # AMCL poses
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
    
    # Recording info
    if 'recording_duration' in data.files:
        print(f"\n--- Recording Info ---")
        print(f"  Duration: {data['recording_duration']} s")
    if 'num_samples' in data.files:
        print(f"  Num samples: {data['num_samples']}")


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
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 plot_navigation_data.py <npz_file>         # Plot navigation data")
        print("  python3 plot_navigation_data.py <npz_file> --aruco # Print ArUco data")
        print("  python3 plot_navigation_data.py <npz_file> --keys  # Print NPZ keys")
        
        # Try latest file
        data_dir = os.path.expanduser('~/navigation_data')
        if os.path.exists(data_dir):
            files = sorted([f for f in os.listdir(data_dir) if f.endswith('.npz')])
            if files:
                latest_file = os.path.join(data_dir, files[-1])
                print(f"\nLatest file: {latest_file}")
                plot_navigation_data(latest_file)
        sys.exit(0)
    
    npz_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        if sys.argv[2] == '--aruco':
            print_aruco_data(npz_file)
        elif sys.argv[2] == '--keys':
            print_npz_keys(npz_file)
    else:
        # Check if it's an aruco recording or navigation data
        data = np.load(npz_file)
        if 'distances' in data.files or 'positions' in data.files:
            print_aruco_data(npz_file)
        else:
            plot_navigation_data(npz_file)


if __name__ == '__main__':
    main()