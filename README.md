# ROS 2 CCSDS Communication Bridge

This package implements a **ROS 2-to-CCSDS communication bridge** that simulates space-to-ground telemetry and telecommand communication using the CCSDS standard. It allows ROS 2 topics to be encoded as CCSDS packets, transmitted over a Starlink-style relay server, and decoded on the ground side to forward to tools like **Open MCT**.

---

##  System Overview

The communication pipeline consists of two main parts:

### 1. `bridge.launch.py` – Uplink from Space Station (Flight Segment)
- **Encodes ROS 2 topics into CCSDS telemetry packets**
- Sends packets over WebSocket to a **Starlink relay server**

### 2. `ground_station.launch.py` – Downlink to Ground Station
- **Receives CCSDS packets** from the relay server
- Decodes them into native ROS 2 messages
- Forwards them to other systems (e.g. Open MCT dashboard)

---

## 📁 Folder Structure

```

demo\_ros\_ccsds\_bridge/
├── config/
│   └── bridge.yaml                   # APID and topic mappings
├── demo\_ros\_ccsds\_bridge/
│   ├── ground/                       # Ground-side receiver and decoder
│   ├── space\_station/               # Space-side encoder and bridge
│   └── **init**.py
├── launch/
│   ├── bridge.launch.py             # Launches space → relay node
│   └── ground\_station.launch.py     # Launches ground ← relay node

````

---

##  Configuration File

Edit the `bridge.yaml` config to define which ROS 2 topics are bridged and how they're mapped to CCSDS APIDs:

```yaml
- ros_topic_name: "/o2_storage"
  ros_type_name: "std_msgs/msg/Float64"
  packet_apid: 44
  communication_type: "TM"  # "TM" = Telemetry
````

---

##  How to Run

### Prerequisites

* ROS 2 (Humble or later)
* `websockets` Python package (`pip install websockets`)
* [spacepackets](https://github.com/robamu-org/python-spacepackets) for CCSDS encoding

---


### 1. Launch the Bridge (Space Segment)

This sends CCSDS packets from ROS 2 topics to the relay:

```bash
ros2 launch demo_ros_ccsds_bridge bridge.launch.py
```

---

### 3. Launch the Ground Station

This receives CCSDS packets, decodes them, and republishes to ROS:

```bash
ros2 launch demo_ros_ccsds_bridge ground_station.launch.py
```

---

##  How It Works

### Encoding Path (bridge.launch.py)

1. Reads topic-to-APID mappings from `bridge.yaml`
2. Subscribes to each ROS 2 topic
3. Encodes messages into CCSDS packets
4. Sends them over WebSocket to the relay server

### Relay Server

* Accepts WebSocket clients from space and ground
* Forwards packets transparently between them

### Decoding Path (ground\_station.launch.py)

1. Receives packets from the relay server
2. Parses CCSDS headers to extract APID and payload
3. Converts payload into a ROS 2 message and republishes

---

##  Testing

You can echo and publish to topics like:

```bash
ros2 topic pub /o2_storage std_msgs/msg/Float64 "data: 18.5"
ros2 topic echo /o2_storage  # On ground side
```

---

##  Telemetry Forwarding to Open MCT (Need to add)

On the ground, decoded topics can be visualized by running:

```bash
npm start  # From the openmct-ros plugin directory
```

And configuring it to receive topics from WebSocket output like:

```json
{
  "topic": "/o2_storage",
  "value": 18.5,
  "timestamp": 1754424273.52
}
```

---

## 📚 Reference

* CCSDS Packet Specification: [https://public.ccsds.org](https://public.ccsds.org)
* WebSocket Docs: [https://websockets.readthedocs.io](https://websockets.readthedocs.io)
* Open MCT: [https://nasa.github.io/openmct/](https://nasa.github.io/openmct/)
* spacepackets Python Library: [https://github.com/robamu-org/python-spacepackets](https://github.com/robamu-org/python-spacepackets)

---



## 🛠️ Future Improvements

* Support for Telecommand (TC) encoding and decoding
* Packet error injection for testing fault tolerance
* Add encryption layer for secure transmission
* Add support for CFDP and USLP

---

## 👨‍🚀 Authors

Developed as part of the **Space Station OS** project.

> Bridging ROS 2 space systems with real-world ground communication standards.

```
