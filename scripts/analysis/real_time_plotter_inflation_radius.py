#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from std_msgs.msg import Float32, Bool
from geometry_msgs.msg import PoseStamped
from rcl_interfaces.srv import GetParameters
from aruco_interfaces.msg import ArucoMarkers
import numpy as np
from datetime import datetime
import os
import math

class PlotRelay(Node):
    def __init__(self):
        super().__init__('plot_relay')
        
        # Publishers
        self.distance_pub = self.create_publisher(Float32, '/goal_distance', 10)
        self.inflation_pub = self.create_publisher(Float32, '/inflation_radius', 10)
        
        # Subscribe to Nav2 feedback
        self.feedback_sub = self.create_subscription(
            NavigateToPose.Impl.FeedbackMessage,
            '/navigate_to_pose/_action/feedback',
            self.feedback_callback,
            10
        )
        
        # Subscribe to critical goal flag from navigation client
        self.critical_goal_sub = self.create_subscription(
            Bool,
            '/critical_goal',
            self.critical_goal_callback,
            10
        )
        
        # Subscribe to goal pose to track target location
        self.goal_pose_sub = self.create_subscription(
            PoseStamped,
            '/goal_pose',
            self.goal_pose_callback,
            10
        )
        
        # Subscribe to ArUco markers directly from pose estimation node
        self.aruco_markers_sub = self.create_subscription(
            ArucoMarkers,
            '/aruco/markers',
            self.aruco_markers_callback,
            10
        )
        
        # Subscribe to ArUco recording start signal from navigation client
        self.aruco_start_sub = self.create_subscription(
            Bool,
            '/start_aruco_recording',
            self.aruco_start_callback,
            10
        )
        
        # Remove service client - not needed anymore!
        # self.aruco_trigger_client = self.create_client(Trigger, '/aruco_pose_estimation/trigger')
        
        # Parameter client for reading inflation radius
        self.param_client = self.create_client(
            GetParameters,
            '/global_costmap/global_costmap/get_parameters'
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
        
        # Read inflation radius periodically
        self.create_timer(0.5, self.publish_inflation)
        
        # Save data periodically (every 5 seconds)
        self.create_timer(5.0, self.save_data)
        
        # Output directory
        self.output_dir = os.path.expanduser('~/navigation_data')
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.get_logger().info(f'PlotRelay node initialized. Data will be saved to: {self.output_dir}')
        self.get_logger().info('Listening for ArUco recording triggers from navigation client')
        self.get_logger().info(f'ArUco recording duration: {self.aruco_recording_duration}s')
        self.get_logger().info(f'Target marker ID: {self.target_marker_id if self.target_marker_id >= 0 else "Any"}')
    
    def critical_goal_callback(self, msg):
        """Handle critical goal flag from navigation client"""
        self.is_critical_goal = msg.data
        
        if self.is_critical_goal:
            self.get_logger().info('Critical goal detected')
        else:
            self.get_logger().info('Non-critical goal detected')
    
    def goal_pose_callback(self, msg):
        """Store the current goal pose"""
        self.goal_pose = msg
        self.get_logger().info(
            f'Goal pose received: ({msg.pose.position.x:.2f}, {msg.pose.position.y:.2f})'
        )
    
    def aruco_markers_callback(self, msg):
        """Handle ArUco markers - extract distance from pose"""
        if not self.is_recording_aruco:
            return
        
        if len(msg.marker_ids) == 0:
            self.get_logger().warn('No markers detected during recording', throttle_duration_sec=2.0)
            return
        
        # Find target marker or use first detected marker
        if self.target_marker_id >= 0:
            try:
                idx = msg.marker_ids.index(self.target_marker_id)
                marker_id = msg.marker_ids[idx]
                pose = msg.poses[idx]
            except (ValueError, IndexError):
                self.get_logger().warn(
                    f'Target marker {self.target_marker_id} not found',
                    throttle_duration_sec=2.0
                )
                return
        else:
            # Use first detected marker
            marker_id = msg.marker_ids[0]
            pose = msg.poses[0]
        
        # Extract Z distance (depth from camera)
        distance = pose.position.z
        
        # Update current distance (for main plotter recording)
        self.current_aruco_distance = distance
        
        # Record data for ArUco-specific analysis
        self.aruco_recorded_distances.append(distance)
        self.aruco_recorded_poses.append(pose)
        self.aruco_recorded_marker_ids.append(marker_id)
        
        elapsed = (self.get_clock().now() - self.aruco_recording_start_time).nanoseconds / 1e9
        
        self.get_logger().info(
            f'📏 Marker {marker_id}: Distance={distance:.3f}m, '
            f'Samples={len(self.aruco_recorded_distances)}, Elapsed={elapsed:.1f}s',
            throttle_duration_sec=1.0
        )
        
        # Check if recording duration completed
        if elapsed >= self.aruco_recording_duration:
            self.stop_aruco_recording()
    
    def aruco_start_callback(self, msg):
        """Handle ArUco recording start signal from navigation client"""
        if msg.data and not self.is_recording_aruco:
            self.get_logger().info('📨 Received ArUco start signal - starting recording')
            self.start_aruco_recording()
    
    def start_aruco_recording(self):
        """Start ArUco pose recording"""
        self.is_recording_aruco = True
        self.aruco_recording_start_time = self.get_clock().now()
        self.aruco_recorded_distances = []
        self.aruco_recorded_poses = []
        self.aruco_recorded_marker_ids = []
        
        self.get_logger().info(f'🎯 Started ArUco recording for {self.aruco_recording_duration}s')
    
    def stop_aruco_recording(self):
        """Stop ArUco recording and save data"""
        if not self.is_recording_aruco:
            return
        
        self.is_recording_aruco = False
        
        num_samples = len(self.aruco_recorded_distances)
        
        self.get_logger().info(f'✓ ArUco recording stopped. Captured {num_samples} samples')
        
        if num_samples > 0:
            # Calculate statistics
            distances = np.array(self.aruco_recorded_distances)
            mean_dist = np.mean(distances)
            std_dist = np.std(distances)
            min_dist = np.min(distances)
            max_dist = np.max(distances)
            
            self.get_logger().info(
                f'📊 Statistics: Mean={mean_dist:.3f}m, Std={std_dist:.3f}m, '
                f'Min={min_dist:.3f}m, Max={max_dist:.3f}m'
            )
            
            # Save ArUco-specific data if enabled
            if self.save_aruco_data:
                self.save_aruco_recording_data(distances)
        else:
            self.get_logger().warn('No ArUco markers detected during recording')
        
        # Reset current distance after recording stops
        self.current_aruco_distance = None
    
    def save_aruco_recording_data(self, distances):
        """Save ArUco-specific recording data"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            aruco_dir = os.path.join(self.output_dir, 'aruco_recordings')
            os.makedirs(aruco_dir, exist_ok=True)
            filename = os.path.join(aruco_dir, f'aruco_recording_{timestamp}.npz')
            
            # Convert poses to arrays
            positions = np.array([[p.position.x, p.position.y, p.position.z] 
                                 for p in self.aruco_recorded_poses])
            orientations = np.array([[p.orientation.x, p.orientation.y, 
                                     p.orientation.z, p.orientation.w] 
                                    for p in self.aruco_recorded_poses])
            
            np.savez(
                filename,
                distances=distances,
                positions=positions,
                orientations=orientations,
                marker_ids=np.array(self.aruco_recorded_marker_ids),
                recording_duration=self.aruco_recording_duration,
                num_samples=len(distances)
            )
            
            self.get_logger().info(f'💾 Saved ArUco recording to: {filename}')
            
        except Exception as e:
            self.get_logger().error(f'Failed to save ArUco recording: {str(e)}')
    
    def feedback_callback(self, msg):
        """Handle Nav2 feedback with distance remaining"""
        distance_remaining = msg.feedback.distance_remaining
        
        # Filter out zero or invalid distances
        if distance_remaining <= 0.0:
            self.get_logger().debug(
                f'Ignoring invalid distance: {distance_remaining:.2f}m',
                throttle_duration_sec=2.0
            )
            return
        
        # Publish distance
        distance_msg = Float32()
        distance_msg.data = distance_remaining
        self.distance_pub.publish(distance_msg)
        
        # Store data in arrays
        current_time = (self.get_clock().now() - self.start_time).nanoseconds / 1e9
        self.time_array.append(current_time)
        self.distance_array.append(distance_remaining)
        self.inflation_array.append(self.current_inflation_radius if self.current_inflation_radius else 0.0)
        self.aruco_distance_array.append(self.current_aruco_distance if self.current_aruco_distance else np.nan)
        
        # Log info with ArUco distance if available
        if self.current_aruco_distance is not None:
            self.get_logger().info(
                f'Distance: {distance_remaining:.2f}m, Inflation: {self.current_inflation_radius:.3f}m, ArUco: {self.current_aruco_distance:.3f}m',
                throttle_duration_sec=1.0
            )
        else:
            self.get_logger().info(
                f'Distance: {distance_remaining:.2f}m, Inflation: {self.current_inflation_radius:.3f}m',
                throttle_duration_sec=1.0
            )
    
    def publish_inflation(self):
        """Read inflation radius from parameter and publish"""
        if not self.param_client.service_is_ready():
            self.get_logger().warn(
                'Parameter service not ready',
                throttle_duration_sec=5.0
            )
            return
        
        try:
            request = GetParameters.Request()
            request.names = ['inflation_layer.inflation_radius']
            
            future = self.param_client.call_async(request)
            future.add_done_callback(self.param_callback)
            
        except Exception as e:
            self.get_logger().error(f'Failed to request inflation radius: {str(e)}')
    
    def param_callback(self, future):
        """Handle parameter response"""
        try:
            response = future.result()
            
            if response.values and len(response.values) > 0:
                inflation_radius = response.values[0].double_value
                self.current_inflation_radius = inflation_radius
                
                # Publish the value
                inflation_msg = Float32()
                inflation_msg.data = inflation_radius
                self.inflation_pub.publish(inflation_msg)
                
                self.get_logger().debug(f'Inflation radius: {inflation_radius:.3f}m')
            else:
                self.get_logger().warn('Empty parameter response')
                
        except Exception as e:
            self.get_logger().error(f'Error reading inflation radius: {str(e)}')
    
    def save_data(self):
        """Save collected data to NPZ file"""
        if len(self.time_array) == 0:
            self.get_logger().debug('No data to save yet')
            return
        
        try:
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = os.path.join(self.output_dir, f'navigation_data_{timestamp}.npz')
            
            # Convert lists to numpy arrays and save
            np.savez(
                filename,
                time=np.array(self.time_array),
                distance=np.array(self.distance_array),
                inflation_radius=np.array(self.inflation_array),
                aruco_distance=np.array(self.aruco_distance_array)
            )
            
            # Count valid ArUco measurements
            aruco_valid = np.sum(~np.isnan(self.aruco_distance_array))
            
            self.get_logger().info(
                f'Saved {len(self.time_array)} data points ({aruco_valid} ArUco measurements) to {filename}'
            )
            
        except Exception as e:
            self.get_logger().error(f'Failed to save data: {str(e)}')
    
    def save_final_data(self):
        """Save final data on shutdown"""
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
                
                # Count valid ArUco measurements
                aruco_valid = np.sum(~np.isnan(self.aruco_distance_array))
                
                self.get_logger().info(
                    f'Final save: {len(self.time_array)} data points ({aruco_valid} ArUco measurements) to {filename}'
                )
            except Exception as e:
                self.get_logger().error(f'Failed to save final data: {str(e)}')

def main():
    rclpy.init()
    node = PlotRelay()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down PlotRelay node')
    finally:
        # Stop ArUco recording if active
        if node.is_recording_aruco:
            node.stop_aruco_recording()
        
        # Save data one last time before shutting down
        node.save_final_data()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()