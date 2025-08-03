from spacepackets.ccsds import PacketType, SpacePacketHeader
import struct

# Simulate a CO2 sensor reading
co2_level = 567.89

# Step 1: Encode the payload (float64 big-endian)
payload = struct.pack(">d", co2_level)  # 8 bytes

# Step 2: Create CCSDS Primary Header
header = SpacePacketHeader(
    packet_type=PacketType.TM,     # Telemetry
    sec_header_flag=False,            # No secondary header
    apid=42,                       # Arbitrary APID for CO2
    seq_flags=3,                   # Unsegmented
    seq_count=1,
    data_len=len(payload) - 1      # Per CCSDS: data_len = (length of data) - 1
)

# Step 3: Combine header and payload
packet_bytes = header.pack() + payload

# Log the packet
print("Encoded CCSDS TM Packet (hex):", packet_bytes.hex())

# Step 4: Decode
# First 6 bytes are always the primary header
raw_header = packet_bytes[:6]
decoded_header = SpacePacketHeader.unpack(raw_header)

# Remaining bytes = payload
raw_payload = packet_bytes[6:]
decoded_value = struct.unpack(">d", raw_payload)[0]

# Print results
print("Decoded Header:")
print(f"  APID: {decoded_header.apid}")
print(f"  Packet Type: {decoded_header.packet_type.name}")
print("Decoded Payload:")
print(f"  CO2 Level: {decoded_value}")
