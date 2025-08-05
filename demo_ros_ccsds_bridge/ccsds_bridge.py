import rclpy 
from rclpy.node import Node
import yaml 
from std_msgs.msg import Float64, Int32, String, Bool 
import os 
import time 
import spacepackets.ccsds as ccsds 
import websockets 
from dataclasses import dataclass 
import json 
import base64 

@dataclass 
class BridgeEntry:
    ros_topic_name: str
    ros_type_name: str
    packet_apid: int
    communication_type: str
    
class CCSDSBridge(Node): 
    def __init__(self,config_file):
        super().__init__('ccsds_bridge') 
        self.config=config_file
        self.bridge_entries= self.load_bridge_data(self.config)
    
    
    def create_subscriber(self,bridge_entry):
        msg_type = self.resolve_message_type(bridge_entry.ros_type_name)
        self.create_subscription(
            msg_type,
            bridge_entry.ros_topic_name,
            lambda msg, e = bridge_entry: self.handle_msg(msg,e),
            10
        )
        
    
    
    def resolve_message_type(self, ros_type_name):
        """Resolve the ROS message type to a specific class."""
        if ros_type_name == 'std_msgs/Float64':
            return Float64
        elif ros_type_name == 'std_msgs/Int32':
            return Int32
        elif ros_type_name == 'std_msgs/String':
            return String
        elif ros_type_name == 'std_msgs/Bool':
            return Bool
        else:
            raise ValueError(f"Unsupported ROS type: {ros_type_name}")
        
    def load_bridge_data(self,yaml_file: str):
        """Load bridge configuration from a YAML file."""
        with open(yaml_file, 'r') as f:
            data = yaml.safe_load(f)

        bridge_data = []
        for entry in data:
            bridge_data.append(BridgeEntry(
                ros_topic_name=entry['ros_topic_name'],
                ros_type_name=entry['ros_type_name'],
                packet_apid=entry['packet_apid'],
                communication_type=entry['communication_type']
            ))
        for entry in data:
            bridge_data.append(bridge_data)
            
        return bridge_data 
    
    def convert_ros_to_ccsds(self, ros_type:str): 
        """Convert ROS message type to CCSDS packet type."""
        if ros_type == 'std_msgs/Float64':
            return ccsds.Float64Packet
        elif ros_type == 'std_msgs/Int32':
            return ccsds.Int32Packet
        elif ros_type == 'std_msgs/String':
            return ccsds.StringPacket
        elif ros_type == 'std_msgs/Bool':
            return ccsds.BoolPacket
        else:
            raise ValueError(f"Unsupported ROS type: {ros_type}")

    def handle_msg(self,msg,e: BridgeEntry):
        """Handle incoming ROS messages and convert them to CCSDS packets."""
        payload = self.convert_ros_to_ccsds(e.ros_type_name)(msg.data)
        header = ccsds.SpacePacketHeader(
            packet_type=ccsds.PacketType.TM if e.communication_type == "TM" else ccsds.PacketType.TC,
            sec_header_flag=False,
            apid=e.packet_apid,
            sequence_count=0,  # Placeholder for sequence count
            data_length=len(payload)
        )
        
        raw_packet= header.pack() + payload 
        encoded= base64.b64encode(raw_packet).decode('utf-8')
        
        out_msg={
            "topic": e.ros_topic_name,
            "apid": e.packet_apid,
            "timestamp": time.time(),
            "ccsds_encoded": encoded
        }
        
        json_str= json.dumps(out_msg)
        