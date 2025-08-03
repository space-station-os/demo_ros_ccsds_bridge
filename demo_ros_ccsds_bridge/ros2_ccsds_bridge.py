#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from spacepackets.ccsds import PacketType, SpacePacketHeader

from std_msgs.msg import Float64  

from demo_ros_ccsds_bridge.bridge_config import load_bridge_config, WebSocketCCSDSPublisher
from demo_ros_ccsds_bridge.message_converter import convert_to_ccsds_payload
import socket

class ROS2CCSDSBridge(Node):
    def __init__(self, config_path):
        super().__init__('ros2_ccsds_bridge')
        self.get_logger().info(f"Loading config from: {config_path}")
        self.ws_client = WebSocketCCSDSPublisher("ws://<ground-ip>:8765")

        self.bridge_entries = load_bridge_config(config_path)

        for entry in self.bridge_entries:
            if entry.ros_type_name == "std_msgs/msg/Float64":
                self.create_subscription(Float64, entry.ros_topic_name,
                                         lambda msg, e=entry: self.handle_msg(msg, e), 10)
                self.get_logger().info(f"Subscribed to {entry.ros_topic_name} (APID {entry.packet_apid})")

    def handle_msg(self, msg, entry):
        payload = convert_to_ccsds_payload(msg, entry.ros_type_name)

        header = SpacePacketHeader(
            packet_type=PacketType.TM if entry.communication_type == "TM" else PacketType.TC,
            sec_header_flag=False,
            apid=entry.packet_apid,
            seq_count=1,
            data_len=len(payload) - 1
        )

        packet = header.pack() + payload

        self.ws_client.send(packet)
        self.get_logger().info_once(f"Packet sent to WebSocket: {packet.hex()}")


        self.get_logger().info(
            f"[CCSDS {entry.communication_type}] {entry.ros_topic_name}: {msg.data} ➝ {packet.hex()}"
        )

def main(args=None):
    import sys
    from pathlib import Path

    rclpy.init(args=args)
    if len(sys.argv) < 2:
        print("Usage: ros2 run demo_communication_bridge ros2_ccsds_bridge.py <config.yaml>")
        return

    config_path = sys.argv[1]
    if not Path(config_path).exists():
        print(f"Error: Config file {config_path} not found")
        return

    node = ROS2CCSDSBridge(config_path)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()