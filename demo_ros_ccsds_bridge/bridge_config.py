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
