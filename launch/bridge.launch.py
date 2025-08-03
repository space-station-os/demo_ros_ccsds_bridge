from launch import LaunchDescription
from launch_ros.actions import Node
import os 
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    config_file = os.path.join(get_package_share_directory('demo_ros_ccsds_bridge'), 'config', 'bridge.yaml')
    return LaunchDescription([
        Node(
            package='demo_ros_ccsds_bridge',
            executable='ccsds_bridge',
            name='ros2_ccsds_bridge',
            output='screen',
            arguments=[config_file]
        )
    ])
