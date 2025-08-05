import asyncio
import websockets
import base64
import json
import struct
from spacepackets.ccsds import SpacePacketHeader

def try_unpack_payload(payload: bytes):
    try:
        if len(payload) == 8:
            value = struct.unpack("<d", payload)[0]
            return f"float64: {value}"
        elif len(payload) == 4:
            value = struct.unpack("<i", payload)[0]
            return f"int32: {value}"
        elif len(payload) == 1:
            value = struct.unpack("<?", payload)[0]
            return f"bool: {value}"
        elif len(payload) == 0:
            return "empty payload"
        else:
            return f"unknown ({len(payload)} bytes): {payload.hex()}"
    except Exception as e:
        return f"unpack error: {e}"

async def listen():
    uri = "ws://localhost:8765"
    print(f"[Client] Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("[Client] Connected to WebSocket server")
            while True:
                msg = await websocket.recv()
                try:
                    data = json.loads(msg)
                    topic = data.get("topic")
                    apid = data.get("apid")
                    encoded = data.get("ccsds_encoded")
                    timestamp = data.get("timestamp")

                    raw_bytes = base64.b64decode(encoded)
                    header = SpacePacketHeader.unpack(raw_bytes[:6])
                    payload = raw_bytes[6:]

                    decoded = try_unpack_payload(payload)

                    print(f"\n[Packet @ {timestamp}]")
                    print(f"Topic      ➝ {topic}")
                    print(f"APID       ➝ {apid}")
                    print(f"Header     ➝ Type: {header.packet_type.name}, Seq: {header.seq_count}, DataLen: {header.data_len}")
                    print(f"Payload    ➝ {decoded}")
                except Exception as e:
                    print(f"[Error] Failed to decode message: {e}")
                    print(f"Raw msg: {msg}")
    except ConnectionRefusedError:
        print("[Client] Failed to connect to WebSocket server. Is the bridge running?")

asyncio.run(listen())
