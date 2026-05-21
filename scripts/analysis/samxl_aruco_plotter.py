#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseArray
import numpy as np
from datetime import datetime
import os


class BagDataRecorder(Node):
    def __init__(self):
        super().__init__('bag_data_recorder')

        self.output_dir = os.path.expanduser('~/navigation_data')
        os.makedirs(self.output_dir, exist_ok=True)

        self.start_time = self.get_clock().now()

        # AMCL
        self.amcl_time, self.amcl_x, self.amcl_y = [], [], []
        self.amcl_qx, self.amcl_qy, self.amcl_qz, self.amcl_qw = [], [], [], []

        # ArUco
        self.aruco_time, self.aruco_x, self.aruco_y, self.aruco_z = [], [], [], []

        self.create_subscription(PoseWithCovarianceStamped, '/amcl_pose',    self.amcl_cb,  10)
        self.create_subscription(PoseArray,                 '/aruco/poses',  self.aruco_cb, 10)

        self.get_logger().info(f'Recording to: {self.output_dir}')

    def elapsed(self):
        return (self.get_clock().now() - self.start_time).nanoseconds / 1e9

    def amcl_cb(self, msg):
        p = msg.pose.pose.position
        o = msg.pose.pose.orientation
        self.amcl_time.append(self.elapsed())
        self.amcl_x.append(p.x);  self.amcl_y.append(p.y)
        self.amcl_qx.append(o.x); self.amcl_qy.append(o.y)
        self.amcl_qz.append(o.z); self.amcl_qw.append(o.w)

    def aruco_cb(self, msg):
        for pose in msg.poses:
            self.aruco_time.append(self.elapsed())
            self.aruco_x.append(pose.position.x)
            self.aruco_y.append(pose.position.y)
            self.aruco_z.append(pose.position.z)  # depth = distance to marker

    def save(self):
        if not any([self.amcl_time, self.aruco_time]):
            self.get_logger().warn('No data to save.')
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        path = os.path.join(self.output_dir, f'bag_recording_{timestamp}.npz')

        np.savez(
            path,
            amcl_time=np.array(self.amcl_time),
            amcl_x=np.array(self.amcl_x),
            amcl_y=np.array(self.amcl_y),
            amcl_qx=np.array(self.amcl_qx),
            amcl_qy=np.array(self.amcl_qy),
            amcl_qz=np.array(self.amcl_qz),
            amcl_qw=np.array(self.amcl_qw),
            aruco_time=np.array(self.aruco_time),
            aruco_x=np.array(self.aruco_x),
            aruco_y=np.array(self.aruco_y),
            aruco_z=np.array(self.aruco_z),
        )
        self.get_logger().info(
            f'Saved to {path}  '
            f'(amcl={len(self.amcl_time)}, aruco={len(self.aruco_time)} samples)'
        )


def main():
    rclpy.init()
    node = BagDataRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.save()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()