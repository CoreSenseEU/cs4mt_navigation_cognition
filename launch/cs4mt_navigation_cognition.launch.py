import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    namespace = LaunchConfiguration('namespace')
    pkg_dir = get_package_share_directory('cs4mt_navigation_cognition')

    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace',
        default_value='',
        description='Namespace')

    # Executable Actions for nthis nodule  here
    # Leaiongthis empty for now to get the structure proper first
    

    # Create the launch description and populate
    ld = LaunchDescription()

    ld.add_action(declare_namespace_cmd)

    # Declare the launch options
    #ld.add_action(cm1_cmd)
    #ld.add_action(cm2_cmd)
    #ld.add_action(cm3_cmd)
    #ld.add_action(cm4_cmd)
    #ld.add_action(cm5_cmd)
    #ld.add_action(m_cmd)

    return ld
