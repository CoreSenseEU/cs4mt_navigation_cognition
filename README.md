# cs4mt_navigation_cognition
CoreSense Navigation Cognition Module

# Dependencies
Humble

# Installation
git clone https://github.com/KeerthiSagarSN/cs4mt_navigation_cognition/

# Launch file for basic set service functionality for reducing inflation radius
ros2 launch cs4mt_navigation_cognition cs4mt_navigation_cognition.launch.py 

# Manual activation of lifecylce node here
ros2 lifecycle set /cs4mt_navigation_cognition_master configure
ros2 lifecycle set /cs4mt_navigation_cognition_master activate


# Dependencies - Third party repos
git clone https://github.com/KeerthiSagarSN/kmriiwa_ros2_bridge_stack


## Launch dependencies for Mobile robot using Gazebo using KMR-IIWA
#### The commands are already listed within the main repo- only relevant launch commands are listed below
ros2 launch kmriiwa_simulation gazebo_coresense.launch.py

ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --qx 0 --qy 0 --qz 0 --qw 1 --frame-id map --child-frame-id kmriiwa_odom & ros2 run tf2_ros static_transform_publisher --x 0 --y 0 --z 0 --qx 0 --qy 0 --qz 0 --qw 1 --frame-id kmriiwa_odom --child-frame-id kmriiwa_base_footprint

ros2 run topic_tools relay /kmriiwa/base/command/cmd_vel /cmd_vel

ros2 launch kmriiwa_navigation kmr_robot_navigation_with_cs.launch.py
## Initialize pose in rviz

## Send goals for robot in Gazebo
cd /kmriiwa_navigation/scripts
python3 send_multiple_goals_gazebo_with_cs.py














