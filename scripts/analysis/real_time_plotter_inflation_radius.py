#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import PoseStamped, PoseWithCovarianceStamped
from rcl_interfaces.srv import GetParameters
from aruco_interfaces.msg import ArucoMarkers
from tf2_ros import Buffer, TransformListener
import numpy as np
from datetime import datetime
import os
import math


class PlotRelay(Node):
    def __init__(self):
        super().__init__('plot_relay')
        
        # TF for robot pose
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        # Current AMCL pose
        self.current_amcl_pose = None
        
        # Publishers
        self.distance_pub = self.create_publisher(Float32, '/goal_distance', 10)
        self.inflation_pub = self.create_publisher(Float32, '/inflation_radius', 10)

        self.declare_parameter('aruco_topic', '/aruco/camera1/markers')
        aruco_topic = self.get_parameter('aruco_topic').value
        
        # Subscribers
        self.feedback_sub = self.create_subscription(
            NavigateToPose.Impl.FeedbackMessage,
            '/navigate_to_pose/_action/feedback',
            self.feedback_callback,
            10
        )
        
        self.critical_goal_sub = self.create_subscription(
            Bool,
            '/critical_goal',
            self.critical_goal_callback,
            10
        )
        
        self.goal_pose_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_pose_callback,
            10
        )
        
        self.aruco_markers_sub = self.create_subscription(
            ArucoMarkers,
            aruco_topic,
            self.aruco_markers_callback,
            10
        )
        
        self.aruco_start_sub = self.create_subscription(
            Bool,
            '/start_aruco_recording',
            self.aruco_start_callback,
            10
        )
        
        self.amcl_pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.amcl_pose_callback,
            10
        )
        
        
        # Store current values
        self.current_inflation_radius = None
        self.is_critical_goal = False
        self.goal_pose = None
        self.current_aruco_distance = None
        
        # ArUco recording state
        self.is_recording_aruco = False
        self.aruco_recording_start_time = None
        self.aruco_recorded_distances = []
        self.aruco_recorded_poses = []
        self.aruco_recorded_marker_ids = []
        self.aruco_recorded_robot_poses = []  # TF poses
        self.aruco_recorded_amcl_poses = []   # AMCL poses
        
        # Parameters for ArUco recording
        self.declare_parameter('aruco_recording_duration', 20.0)
        self.declare_parameter('target_marker_id', -1)
        self.declare_parameter('save_aruco_data', True)
        
        self.aruco_recording_duration = self.get_parameter('aruco_recording_duration').value
        self.target_marker_id = self.get_parameter('target_marker_id').value
        self.save_aruco_data = self.get_parameter('save_aruco_data').value
        
        # Data storage arrays
        self.distance_array = []
        self.inflation_array = []
        self.aruco_distance_array = []
        self.time_array = []
        self.start_time = self.get_clock().now()
        
        self.create_timer(0.5, self.publish_inflation)
        self.create_timer(5.0, self.save_data)
        
        self.output_dir = os.path.expanduser('~/navigation_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.get_logger().info(f'PlotRelay node initialized. Data will be saved to: {self.output_dir}')

    def get_robot_pose(self):
        """Get robot pose from TF (map -> base_link)."""
        try:
            t = self.tf_buffer.lookup_transform('map', 'base_link', rclpy.time.Time())
            x = t.transform.translation.x
            y = t.transform.translation.y
            q = t.transform.rotation
            yaw = math.atan2(2.0 * (q.w * q.z + q.x * q.y),
                            1.0 - 2.0 * (q.y * q.y + q.z * q.z))
            return x, y, yaw
        except Exception:
            return None

    def amcl_pose_callback(self, msg):
        """Store latest AMCL pose (full pose + covariance)."""
        p = msg.pose.pose.position
        q = msg.pose.pose.orientation
        self.current_amcl_pose = {
            'position': (p.x, p.y, p.z),
            'orientation': (q.x, q.y, q.z, q.w),
            'covariance': msg.pose.covariance
        }

    def critical_goal_callback(self, msg):
        self.is_critical_goal = msg.data
    
    def goal_pose_callback(self, msg):
        self.goal_pose = msg

    def aruco_markers_callback(self, msg):
        if not self.is_recording_aruco:
            return
        
        if len(msg.marker_ids) == 0:
            return
        
        if self.target_marker_id >= 0:
            try:
                idx = msg.marker_ids.index(self.target_marker_id)
                marker_id = msg.marker_ids[idx]
                pose = msg.poses[idx]
            except (ValueError, IndexError):
                return
        else:
            marker_id = msg.marker_ids[0]
            pose = msg.poses[0]
        
        distance = pose.position.z
        self.current_aruco_distance = distance
        
        # Record all data
        self.aruco_recorded_distances.append(distance)
        self.aruco_recorded_poses.append(pose)
        self.aruco_recorded_marker_ids.append(marker_id)
        self.aruco_recorded_robot_poses.append(self.get_robot_pose())
        self.aruco_recorded_amcl_poses.append(self.current_amcl_pose)
        
        elapsed = (self.get_clock().now() - self.aruco_recording_start_time).nanoseconds / 1e9
        if elapsed >= self.aruco_recording_duration:
            self.stop_aruco_recording()
    
    def aruco_start_callback(self, msg):
        if msg.data and not self.is_recording_aruco:
            self.start_aruco_recording()
    
    def start_aruco_recording(self):
        self.is_recording_aruco = True
        self.aruco_recording_start_time = self.get_clock().now()
        self.aruco_recorded_distances = []
        self.aruco_recorded_poses = []
        self.aruco_recorded_marker_ids = []
        self.aruco_recorded_robot_poses = []
        self.aruco_recorded_amcl_poses = []
        self.get_logger().info(f'Started ArUco recording for {self.aruco_recording_duration}s')
    
    def stop_aruco_recording(self):
        if not self.is_recording_aruco:
            return
        
        self.is_recording_aruco = False
        num_samples = len(self.aruco_recorded_distances)
        self.get_logger().info(f'ArUco recording stopped. Captured {num_samples} samples')
        
        if num_samples > 0 and self.save_aruco_data:
            self.save_aruco_recording_data()
        
        self.current_aruco_distance = None
    
    def save_aruco_recording_data(self):
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            aruco_dir = os.path.join(self.output_dir, 'aruco_recordings')
            os.makedirs(aruco_dir, exist_ok=True)
            filename = os.path.join(aruco_dir, f'aruco_recording_{timestamp}.npz')
            
            # ArUco marker poses
            positions = np.array([[p.position.x, p.position.y, p.position.z] 
                                for p in self.aruco_recorded_poses])
            orientations = np.array([[p.orientation.x, p.orientation.y, 
                                    p.orientation.z, p.orientation.w] 
                                    for p in self.aruco_recorded_poses])
            
            # Robot poses from TF (x, y, yaw)
            tf_poses = np.array([
                [p[0], p[1], p[2]] if p else [np.nan, np.nan, np.nan]
                for p in self.aruco_recorded_robot_poses
            ])
            
            # AMCL poses - full (x, y, z, qx, qy, qz, qw)
            amcl_positions = np.array([
                list(p['position']) if p else [np.nan, np.nan, np.nan]
                for p in self.aruco_recorded_amcl_poses
            ])
            amcl_orientations = np.array([
                list(p['orientation']) if p else [np.nan, np.nan, np.nan, np.nan]
                for p in self.aruco_recorded_amcl_poses
            ])
            amcl_covariances = np.array([
                list(p['covariance']) if p else [np.nan] * 36
                for p in self.aruco_recorded_amcl_poses
            ])
            
            np.savez(
                filename,
                distances=np.array(self.aruco_recorded_distances),
                positions=positions,
                orientations=orientations,
                marker_ids=np.array(self.aruco_recorded_marker_ids),
                tf_poses=tf_poses,
                amcl_positions=amcl_positions,
                amcl_orientations=amcl_orientations,
                amcl_covariances=amcl_covariances,
                recording_duration=self.aruco_recording_duration,
                num_samples=len(self.aruco_recorded_distances)
            )
            
            self.get_logger().info(f'Saved ArUco recording to: {filename}')
            
        except Exception as e:
            self.get_logger().error(f'Failed to save ArUco recording: {str(e)}')

    def feedback_callback(self, msg):
        distance_remaining = msg.feedback.distance_remaining
        if distance_remaining <= 0.0:
            return
        
        distance_msg = Float32()
        distance_msg.data = distance_remaining
        self.distance_pub.publish(distance_msg)
        
        current_time = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        self.time_array.append(current_time)
        self.distance_array.append(distance_remaining)
        self.inflation_array.append(self.current_inflation_radius if self.current_inflation_radius else 0.0)
        self.aruco_distance_array.append(self.current_aruco_distance if self.current_aruco_distance else np.nan)
    
    def publish_inflation(self):
        if not self.param_client.service_is_ready():
            return
        
        try:
            request = GetParameters.Request()
            request.names = ['inflation_layer.inflation_radius']
            future = self.param_client.call_async(request)
            future.add_done_callback(self.param_callback)
        except Exception as e:
            self.get_logger().error(f'Failed to request inflation radius: {str(e)}')
    
    def param_callback(self, future):
        try:
            response = future.result()
            if response.values and len(response.values) > 0:
                self.current_inflation_radius = response.values[0].double_value
                inflation_msg = Float32()
                inflation_msg.data = self.current_inflation_radius
                self.inflation_pub.publish(inflation_msg)
        except Exception as e:
            self.get_logger().error(f'Error reading inflation radius: {str(e)}')
    
    def save_data(self):
        if len(self.time_array) == 0:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f'navigation_data_{timestamp}.npz')
            
            np.savez(
                filename,
                time=np.array(self.time_array),
                distance=np.array(self.distance_array),
                inflation_radius=np.array(self.inflation_array),
                aruco_distance=np.array(self.aruco_distance_array)
            )
            
            self.get_logger().info(f'Saved {len(self.time_array)} data points to {filename}')
        except Exception as e:
            self.get_logger().error(f'Failed to save data: {str(e)}')
    
    def save_final_data(self):
        if len(self.time_array) > 0:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f'navigation_data_final_{timestamp}.npz')
            
            try:
                np.savez(
                    filename,
                    time=np.array(self.time_array),
                    distance=np.array(self.distance_array),
                    inflation_radius=np.array(self.inflation_array),
                    aruco_distance=np.array(self.aruco_distance_array)
                )
                self.get_logger().info(f'Final save: {len(self.time_array)} data points to {filename}')
            except Exception as e:
                self.get_logger().error(f'Failed to save final data: {str(e)}')


def main():
    rclpy.init()
    node = PlotRelay()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node.is_recording_aruco:
            node.stop_aruco_recording()
        node.save_final_data()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()