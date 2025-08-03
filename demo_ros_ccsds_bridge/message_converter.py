import struct
from std_msgs.msg import Float64


def convert_to_ccsds_payload(msg, ros_type: str) -> bytes:
    if ros_type == 'std_msgs/msg/Float64':
        return struct.pack(">d", msg.data)
    raise NotImplementedError(f"Conversion for {ros_type} not implemented")
