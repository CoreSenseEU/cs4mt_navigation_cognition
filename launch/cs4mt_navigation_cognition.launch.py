##################################################################
# Copyright 2024 Intelligent Robotics Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##################################################################

# Copyright 2025 IMR Robotics & Automation Group
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##################################################################

# Reference of this launch file is from cs4home_sound_project

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    #namespace = LaunchConfiguration('namespace')
    
    # Get package directories
    pkg_dir = get_package_share_directory('cs4mt_navigation_cognition')
    #core_pkg_dir = get_package_share_directory('cs4home_core')
    
    # Path to params file in config folder
    config_file = os.path.join(pkg_dir, 'config', 'params.yaml')
    
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace'
    )
    
    # CognitiveModule node with configuration
    # THis one works- use as funcitoning code
    # cm1_cmd = Node(
    #     package='cs4mt_navigation_cognition',
    #     executable='MTNavigationCognitiveModule',
    #     name='navigation_cognitive_module',
    #     #namespace=namespace,
    #     output='screen',
    #     #parameters=[config_file],
    #     # Optional: Add remappings if needed
    #     # remappings=[
    #     #     ('/image_raw', '/camera/image_raw'),
    #     #     ('/detections', '/processed_detections')
    #     # ]
    # )


    # Master node - Should i just launch master and everything launches by itself
    # Reference of this structure is from cs4home_sound_project
    # Need to clariffy with Esteher, carlos/paco
    master_cmd = Node(
        package='cs4mt_navigation_cognition',
        executable='MTNavigationCognitiveMaster',
        name='cs4mt_navigation_cognition_master',
        output='screen',
        parameters=[config_file],
    )
    # goal_cognition_cmd = Node(
    # package='cs4mt_navigation_cognition',
    # executable='goal_cognition_module',
    # name='goal_cognition',
    # output='screen',
    # #parameters=[config_file],
    # )

    # dynamic_reconfig_cmd = Node(
    #     package='cs4mt_navigation_cognition',
    #     executable='dynamic_reconfigure_nav_module',
    #     name='dynamic_reconfigure_nav',
    #     output='screen',
    #     parameters=[config_file],
    # )

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(declare_namespace_cmd)
    ld.add_action(master_cmd) # Laujnch the master node for the navigation cog
    #ld.add_action(cm1_cmd)
    #ld.add_action(goal_cognition_cmd )
    # ld.add_action(dynamic_reconfig_cmd)
    
    return ld
