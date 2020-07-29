#!/usr/bin/env python3
from gpiozero import DigitalOutputDevice
from time import sleep
import paho.mqtt.client as mqtt
import sys

MQTT_URL="192.168.1.3"
MQTT_PORT=1883
MQTT_KEEPALIVE=60
# Topic on which to receive state commands (activate vs deactivate)
MQTT_STATE_TOPIC="relay/state"
# Topic on which to confirm receipt and action taken (activated vs deactivated)
MQTT_STATUS_TOPIC="relay/status"
MQTT_LWT_TOPIC="relay/lwt"

RELAY_GPIO=21

AT_MOST_ONCE=0
AT_LEAST_ONCE=1
EXACTLY_ONCE=2

current_state = "deactivated"
# set up the relay
print(f"Setting up pin {RELAY_GPIO}")
relay = DigitalOutputDevice(RELAY_GPIO)
relay.off()

def new_state(state):
    global current_state
    next_state = f"{state}d"
    if next_state == current_state:
        print(f"Already in correct state: {current_state}")
        return False
    current_state = next_state

    if current_state == "activated":
        relay.on()
    else:
        relay.off()
    return True

def on_connect(c, userdata, flags, rc):
    print(f"Connected to MQTT broker: {rc}")

    c.publish(MQTT_STATUS_TOPIC, current_state, qos=AT_LEAST_ONCE, retain=True)
    # subscribe to the state topic
    c.subscribe(MQTT_STATE_TOPIC, qos=AT_LEAST_ONCE)

    # announce availability
    c.publish(MQTT_LWT_TOPIC, "connected", qos=AT_LEAST_ONCE, retain=True)

def on_message(c, userdata, msg):
    payload = msg.payload.decode('UTF-8').lower()

    if not payload in ["activate", "deactivate"]:
        print(f"Received unexpected message \"{payload}\" from {MQTT_STATE_TOPIC}", file=sys.stderr)
        return
    if new_state(payload):
        print(f"Relay {payload}d")
        c.publish(MQTT_STATUS_TOPIC, f"{payload}d", qos=AT_LEAST_ONCE, retain=True)

# set up the MQTT client
print("Setting up MQTT client")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.enable_logger()

# set a LWT
client.will_set(MQTT_LWT_TOPIC, "disconnected", qos=AT_LEAST_ONCE, retain=True)

client.connect(MQTT_URL, MQTT_PORT, MQTT_KEEPALIVE)

# Steady state
client.loop_forever()
