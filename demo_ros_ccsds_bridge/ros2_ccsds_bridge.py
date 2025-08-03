#!/usr/bin/env python3
<<<<<<< HEAD

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Int32, String, Bool
from dataclasses import dataclass
from typing import List
import yaml
import asyncio
import threading
import struct
import websockets
import base64
import json
import time
import os
from functools import partial
from spacepackets.ccsds import PacketType, SpacePacketHeader
from pathlib import Path

# ------------------------
# Configuration Data
# ------------------------

@dataclass
class BridgeEntry:
    ros_topic_name: str
    ros_type_name: str
    packet_apid: int
    communication_type: str  # "TM" or "TC"

def load_bridge_config(yaml_file: str) -> List[BridgeEntry]:
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    return [
        BridgeEntry(
            ros_topic_name=entry['ros_topic_name'],
            ros_type_name=entry['ros_type_name'],
            packet_apid=entry['packet_apid'],
            communication_type=entry['communication_type']
        )
        for entry in data
    ]

# ------------------------
# WebSocket Broadcast Server
# ------------------------

class CCSDSWebSocketServer:
    def __init__(self, host="0.0.0.0", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.ready = threading.Event()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.thread.start()
        self.ready.wait()
        

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._run_server())


    async def _run_server(self):
        print(f"[WebSocket] Starting at ws://{self.host}:{self.port}")

        async def connection_handler(websocket, path):
            self.clients.add(websocket)
            print("[WebSocket] Client connected")
            try:
                async for message in websocket:
                    print(f"[WebSocket] Received: {message}")
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.clients.remove(websocket)
                print("[WebSocket] Client disconnected")

        self.ready.set()

        async with websockets.serve(connection_handler, self.host, self.port):
            await asyncio.Future()



    def broadcast(self, data: str):
        if self.clients:
            asyncio.run_coroutine_threadsafe(self._broadcast(data), self.loop)

    async def _broadcast(self, data: str):
        for client in self.clients.copy():
            try:
                await client.send(data)
            except:
                self.clients.remove(client)

# ------------------------
# ROS 2 Message ➜ CCSDS Payload Conversion
# ------------------------

def convert_to_ccsds_payload(msg, ros_type: str) -> bytes:
    if ros_type == 'std_msgs/msg/Float64':
        return struct.pack("<d", msg.data)
    elif ros_type == 'std_msgs/msg/Int32':
        return struct.pack("<i", msg.data)
    elif ros_type == 'std_msgs/msg/Bool':
        return struct.pack("<?", msg.data)
    elif ros_type == 'std_msgs/msg/String':
        return msg.data.encode('utf-8')
    else:
        raise NotImplementedError(f"[CCSDS Bridge] No conversion for type: {ros_type}")

# ------------------------
# ROS 2 Node Definition
# ------------------------
=======
import rclpy
from rclpy.node import Node
from spacepackets.ccsds import PacketType, SpacePacketHeader

from std_msgs.msg import Float64  

from demo_ros_ccsds_bridge.bridge_config import load_bridge_config, WebSocketCCSDSPublisher
from demo_ros_ccsds_bridge.message_converter import convert_to_ccsds_payload
import socket
>>>>>>> 0a974b9 (Uplink commit)

class ROS2CCSDSBridge(Node):
    def __init__(self, config_path):
        super().__init__('ros2_ccsds_bridge')
<<<<<<< HEAD

        self.ws_server = CCSDSWebSocketServer()
        self.get_logger().info(f"Loading config from: {config_path}")
        self.bridge_entries = load_bridge_config(config_path)

        for entry in self.bridge_entries:
            self.create_subscriber(entry)

    def create_subscriber(self, entry: BridgeEntry):
        msg_type = self.resolve_msg_type(entry.ros_type_name)
        self.create_subscription(
            msg_type,
            entry.ros_topic_name,
            lambda msg, e=entry: self.handle_msg(msg, e),
            10
        )
        self.get_logger().info(f"Subscribed to {entry.ros_topic_name} (APID {entry.packet_apid})")

    def resolve_msg_type(self, ros_type: str):
        if ros_type == 'std_msgs/msg/Float64':
            return Float64
        elif ros_type == 'std_msgs/msg/Int32':
            return Int32
        elif ros_type == 'std_msgs/msg/Bool':
            return Bool
        elif ros_type == 'std_msgs/msg/String':
            return String
        else:
            raise NotImplementedError(f"[CCSDS Bridge] Unknown ROS 2 type: {ros_type}")

    def handle_msg(self, msg, entry: BridgeEntry):
        payload = convert_to_ccsds_payload(msg, entry.ros_type_name)
=======
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

>>>>>>> 0a974b9 (Uplink commit)
        header = SpacePacketHeader(
            packet_type=PacketType.TM if entry.communication_type == "TM" else PacketType.TC,
            sec_header_flag=False,
            apid=entry.packet_apid,
            seq_count=1,
            data_len=len(payload) - 1
        )
<<<<<<< HEAD
        raw_packet = header.pack() + payload
        encoded = base64.b64encode(raw_packet).decode('utf-8')

        out_msg = {
            "topic": entry.ros_topic_name,
            "apid": entry.packet_apid,
            "timestamp": time.time(),
            "ccsds_encoded": encoded
        }

        json_str = json.dumps(out_msg)
        self.ws_server.broadcast(json_str)

        self.get_logger().info(
            f"[CCSDS {entry.communication_type}] {entry.ros_topic_name}: {msg.data} ➔ {raw_packet.hex()}"
        )

# ------------------------
# Entry Point
# ------------------------

def main(args=None):
    import sys
    rclpy.init(args=args)

    if len(sys.argv) < 2:
        print("Usage: ros2 run <your_package> ros2_ccsds_bridge.py <config.yaml>")
=======

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
>>>>>>> 0a974b9 (Uplink commit)
        return

    config_path = sys.argv[1]
    if not Path(config_path).exists():
        print(f"Error: Config file {config_path} not found")
        return

<<<<<<< HEAD
    print(f"Starting ROS 2 CCSDS Bridge with config: {config_path}")
    print(f"WebSocket server will run at ws://0.0.0.0:8765 or ws://localhost:8765")
=======
>>>>>>> 0a974b9 (Uplink commit)
    node = ROS2CCSDSBridge(config_path)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> 0a974b9 (Uplink commit)
