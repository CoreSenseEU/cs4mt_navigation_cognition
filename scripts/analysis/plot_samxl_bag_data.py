#!/usr/bin/env python3
import numpy as np
import sys
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot_bag_data(npz_file):
    data = np.load(npz_file)

    amcl_time = data['amcl_time']
    amcl_x    = data['amcl_x']
    amcl_y    = data['amcl_y']
    aruco_time = data['aruco_time']
    aruco_x    = data['aruco_x']
    aruco_y    = data['aruco_y']
    aruco_z    = data['aruco_z']

    print(f"Loaded from {npz_file}")
    print(f"  AMCL  : {len(amcl_time)} samples")
    print(f"  ArUco : {len(aruco_time)} samples")

    fig, axes = plt.subplots(5, 1, figsize=(12, 18))
    fig.suptitle(f'Bag Recording — {os.path.basename(npz_file)}', fontsize=13)

    # --- AMCL XY trajectory ---
    ax = axes[0]
    ax.plot(amcl_x, amcl_y, 'b-', linewidth=1.5, label='AMCL trajectory')
    ax.scatter(amcl_x[0],  amcl_y[0],  color='green', zorder=5, label='start')
    ax.scatter(amcl_x[-1], amcl_y[-1], color='red',   zorder=5, label='end')
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('Robot trajectory (AMCL)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal')

    # --- AMCL X and Y vs time ---
    ax = axes[1]
    ax.plot(amcl_time, amcl_x, label='X', linewidth=1.5)
    ax.plot(amcl_time, amcl_y, label='Y', linewidth=1.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Position (m)')
    ax.set_title('AMCL X / Y vs time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- ArUco XY position vs time ---
    ax = axes[2]
    ax.plot(aruco_time, aruco_x, label='ArUco X', linewidth=1.5)
    ax.plot(aruco_time, aruco_y, label='ArUco Y', linewidth=1.5)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Position (m)')
    ax.set_title('ArUco marker X / Y vs time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- ArUco distance (z) vs time ---
    ax = axes[3]
    ax.plot(aruco_time, aruco_z, color='darkorange', linewidth=1.5, label='Distance (z)')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Distance (m)')
    ax.set_title('ArUco marker distance vs time')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # --- ArUco distance histogram ---
    ax = axes[4]
    ax.hist(aruco_z, bins=40, color='darkorange', edgecolor='white', alpha=0.85)
    ax.axvline(np.mean(aruco_z),   color='red',   linestyle='--', linewidth=1.5, label=f'Mean  {np.mean(aruco_z):.3f} m')
    ax.axvline(np.median(aruco_z), color='blue',  linestyle='--', linewidth=1.5, label=f'Median {np.median(aruco_z):.3f} m')
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('Count')
    ax.set_title('ArUco distance distribution')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_image = npz_file.replace('.npz', '.png')
    plt.savefig(output_image, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {output_image}")
    print(f"\nArUco distance stats:")
    print(f"  mean   : {np.mean(aruco_z):.4f} m")
    print(f"  median : {np.median(aruco_z):.4f} m")
    print(f"  std    : {np.std(aruco_z):.4f} m")
    print(f"  min    : {np.min(aruco_z):.4f} m")
    print(f"  max    : {np.max(aruco_z):.4f} m")

    try:
        matplotlib.use('TkAgg')
        plt.show()
    except Exception:
        print("Interactive display not available, image saved successfully")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        data_dir = os.path.expanduser('~/navigation_data')
        if os.path.exists(data_dir):
            files = sorted([f for f in os.listdir(data_dir) if f.startswith('bag_recording') and f.endswith('.npz')])
            if files:
                latest = os.path.join(data_dir, files[-1])
                print(f"No file specified — using latest: {latest}")
                plot_bag_data(latest)
            else:
                print(f"No bag_recording NPZ files found in {data_dir}")
        sys.exit(0)

    plot_bag_data(sys.argv[1])