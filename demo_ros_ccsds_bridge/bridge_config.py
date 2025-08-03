<<<<<<< HEAD
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
=======
import yaml
from dataclasses import dataclass
from typing import List
import asyncio
import websockets
import threading


@dataclass
class BridgeEntry:
    ros_topic_name: str
    ros_type_name: str
    packet_apid: int
    communication_type: str  # "TM" or "TC"

class WebSocketCCSDSPublisher:
    def __init__(self, uri="ws://localhost:8765"):
        self.uri = uri
        self.loop = asyncio.new_event_loop()
        self.queue = asyncio.Queue()
        threading.Thread(target=self._start_loop, daemon=True).start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        try:
            async with websockets.connect(self.uri) as ws:
                while True:
                    packet = await self.queue.get()
                    await ws.send(packet)
        except Exception as e:
            print(f"[WebSocket] Error: {e}")

    def send(self, data: bytes):
        asyncio.run_coroutine_threadsafe(self.queue.put(data), self.loop)


def load_bridge_config(yaml_file: str) -> List[BridgeEntry]:
    with open(yaml_file, 'r') as f:
        data = yaml.safe_load(f)

    bridges = []
    for entry in data:
        bridges.append(BridgeEntry(
            ros_topic_name=entry['ros_topic_name'],
            ros_type_name=entry['ros_type_name'],
            packet_apid=entry['packet_apid'],
            communication_type=entry['communication_type']
        ))

    return bridges
>>>>>>> 0a974b9 (Uplink commit)
