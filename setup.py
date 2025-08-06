from setuptools import find_packages, setup

package_name = 'demo_ros_ccsds_bridge'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/bridge.launch.py', 'launch/ground_station.launch.py']),
        ('share/' + package_name + '/config', ['config/bridge.yaml']),
        ('share/' + package_name + '/starlink', ['starlink/starlink_relay.py']),
    ],
    install_requires=['setuptools','websockets','spacepackets'],
    zip_safe=True,
    maintainer='siddarth',
    maintainer_email='siddarth.dayasagar@gmail.com',
    description='ros-ccsds bridge demo package',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'space_bridge = demo_ros_ccsds_bridge.space_station.encoder:main',
            'ground_receiver = demo_ros_ccsds_bridge.ground.receiver:main',
        ],
    },
)
