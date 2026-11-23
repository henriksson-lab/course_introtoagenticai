#!/usr/bin/env python3
"""Generate the synthetic USB capture for the exercise "decode an instrument protocol"
(Track: Lab instruments and hardware).

Output: lumoplate-capture.sqlite (and lumoplate-capture-events.csv, a readable copy of
the annotation table) in the folder of this script.

The instrument, the "LumoPlate 3000" absorbance plate reader, is FICTIONAL. Its protocol
was invented for this exercise. Nothing here comes from a real vendor.

THIS FILE CONTAINS THE ANSWER. Participants copy only the .sqlite file to their own
folder and do not show this script to the agent.

Protocol (the answer key, also given in the exercise's collapsed callout):
  frame    = 0xA5 | cmd | len | payload (len bytes) | chk
  chk      = (0x100 - (cmd + len + sum(payload))) & 0xFF   (bytes cmd..chk sum to 0 mod 256)
  host -> device on bulk OUT endpoint 0x02, device -> host on bulk IN endpoint 0x82
  reply cmd = request cmd | 0x80
  0x01 HELLO        ()                      -> 0x81  ASCII firmware version
  0x10 GET_STATUS   ()                      -> 0x90  state u8, temperature f32 LE, door u8
  0x21 SET_TEMP     setpoint f32 LE         -> 0xA1  0x00 (ok)
  0x22 SET_SHAKE    mode u8, seconds u16 LE -> 0xA2  0x00
  0x30 DOOR         0 = close, 1 = open     -> 0xB0  0x00
  0x40 START_READ   wavelength u16 LE, plate type u8 -> 0xC0 0x00
  0x41 GET_ROW      row u8 (0..7 = A..H)    -> 0xC1  row u8 + 12 x f32 LE absorbance
  0x50 STOP         ()                      -> 0xD0  0x00
  state: 0 idle, 1 heating, 2 shaking, 3 reading, 4 data ready
Noise: a USB mouse (device 3, interrupt IN 0x81, 4-byte HID reports) on the same bus,
enumeration control transfers for the plate reader (device 5) at the start, and short
zero-length bulk IN packets.

Python standard library only. Deterministic (fixed random seed).
"""
import csv
import os
import random
import sqlite3
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "lumoplate-capture.sqlite")
EVCSV = os.path.join(HERE, "lumoplate-capture-events.csv")

rng = random.Random(3000)
packets = []   # (t_ms, device, endpoint, direction, transfer, data bytes)
events = []    # (t_ms, kind, description)

DEV = 5
MOUSE = 3


def frame(cmd, payload=b""):
    body = bytes([cmd, len(payload)]) + payload
    chk = (0x100 - sum(body)) & 0xFF
    return b"\xA5" + body + bytes([chk])


def send(t, cmd, payload=b"", reply_payload=b"\x00", delay=None):
    """Host request, then the device reply a few ms later. Returns time after reply."""
    packets.append((t, DEV, 0x02, "OUT", "bulk", frame(cmd, payload)))
    d = delay if delay is not None else rng.randint(2, 6)
    packets.append((t + d, DEV, 0x82, "IN", "bulk", frame(cmd | 0x80, reply_payload)))
    return t + d


def f32(x):
    return struct.pack("<f", x)


# ---------------------------------------------------------------- instrument state
state = {"temp": 22.4, "set": None, "door": 0, "st": 0, "busy_until": 0, "after": 0}


def temp_at(t):
    return state["temp"]


def status_payload(t):
    st = state["st"]
    if state["busy_until"] and t >= state["busy_until"]:
        st = state["after"]
        state["st"] = st
        state["busy_until"] = 0
    return bytes([st]) + f32(round(state["temp"], 2)) + bytes([state["door"]])


def step_temperature():
    """Called once per second: move towards the setpoint, with a little noise."""
    if state["set"] is None:
        state["temp"] += rng.uniform(-0.02, 0.02)
        return
    diff = state["set"] - state["temp"]
    if abs(diff) > 0.15:
        state["temp"] += max(-0.35, min(0.35, diff * 0.12))
        if state["st"] == 0:
            state["st"] = 1
    else:
        state["temp"] = state["set"] + rng.uniform(-0.05, 0.05)
        if state["st"] == 1:
            state["st"] = 0


# ---------------------------------------------------------------- plate data
# A dilution series in columns 1-11, blanks in column 12; replicates in rows A-H.
plate = []
for r in range(8):
    row = []
    for c in range(12):
        if c == 11:
            v = 0.045 + rng.uniform(-0.004, 0.004)
        else:
            v = 0.05 + 2.4 * (0.62 ** c) + rng.uniform(-0.03, 0.03)
        row.append(round(v, 3))
    plate.append(row)

# ---------------------------------------------------------------- timeline
script = {}   # second -> list of actions (callables)
T_END = 420  # seconds of capture


def at(sec, fn):
    script.setdefault(sec, []).append(fn)


def note(t, kind, text):
    events.append((t, kind, text))


# Enumeration of the plate reader (noise: standard USB control transfers)
def enumerate_device(t):
    for i, (req, data) in enumerate([
        ("80 06 00 01 00 00 12 00", "12 01 00 02 FF 00 00 40 34 12 00 30 01 01 01 02 03 01"),
        ("80 06 00 02 00 00 20 00", "09 02 20 00 01 01 00 80 32 09 04 00 00 02 FF 00 00 00 07 05 02 02 40 00 00 07 05 82 02 40 00 00"),
        ("00 09 01 00 00 00 00 00", ""),
    ]):
        packets.append((t + 3 * i, DEV, 0x00, "OUT", "control", bytes.fromhex(req)))
        packets.append((t + 3 * i + 1, DEV, 0x80, "IN", "control", bytes.fromhex(data)))


at(2, lambda t: note(t, "note", "LumoPlate 3000 switched on and plugged in"))
at(3, enumerate_device)
at(6, lambda t: note(t, "click", "user opened the LumoPlate Control app"))
def connect(t):
    note(t, "click", "user clicked Connect; app shows 'Connected, firmware 2.4.1'")
    send(t + 40, 0x01, b"", b"LP3000 fw 2.4.1")


at(9, connect)


def set_temp(value):
    def fn(t):
        note(t, "click", f"user set incubation temperature to {value:.1f} °C and clicked Apply")
        send(t + 25, 0x21, f32(value))
        state["set"] = value
    return fn


def door(open_):
    def fn(t):
        note(t, "click", "user clicked Open door" if open_ else "user clicked Close door")
        send(t + 30, 0x30, bytes([1 if open_ else 0]))
        state["door"] = 1 if open_ else 0
    return fn


def shake(mode_name, mode, secs):
    def fn(t):
        note(t, "click", f"user set shaking: {mode_name}, {secs} s, and clicked Shake")
        send(t + 20, 0x22, bytes([mode]) + struct.pack("<H", secs))
        state["st"] = 2
        state["busy_until"] = t + secs * 1000
        state["after"] = 0
    return fn


def start_read(nm):
    def fn(t):
        note(t, "click", f"user selected wavelength {nm} nm, plate type '96-well flat' and clicked Start")
        send(t + 35, 0x40, struct.pack("<H", nm) + bytes([1]))
        state["st"] = 3
        state["busy_until"] = t + 22000
        state["after"] = 4
    return fn


def fetch_results(t):
    tt = t + 50
    for r in range(8):
        payload = bytes([r]) + b"".join(f32(v) for v in plate[r])
        tt = send(tt, 0x41, bytes([r]), payload) + rng.randint(3, 8)
    note(tt + 400, "screenshot", f"results table shown: A1 = {plate[0][0]:.3f}, "
         f"A12 = {plate[0][11]:.3f}, H1 = {plate[7][0]:.3f}, D6 = {plate[3][5]:.3f}")
    state["st"] = 0


def stop(t):
    note(t, "click", "user clicked Stop")
    send(t + 20, 0x50)
    state["st"] = 0
    state["busy_until"] = 0


at(20, set_temp(37.0))
at(95, door(True))
at(110, lambda t: note(t, "note", "user put a 96-well plate in the drawer"))
at(118, door(False))
at(130, shake("orbital", 2, 30))
at(175, start_read(450))
at(199, fetch_results)
at(230, start_read(600))
at(240, stop)
at(250, lambda t: note(t, "note", "user: 'I pressed Stop by mistake, the 600 nm read was aborted'"))
at(300, set_temp(25.0))
at(340, door(True))
at(355, door(False))
at(400, lambda t: note(t, "click", "user clicked Disconnect and closed the app"))

connected = False
for sec in range(T_END):
    t0 = sec * 1000
    for fn in script.get(sec, []):
        fn(t0 + rng.randint(0, 300))
    if sec == 10:
        connected = True
    if sec == 400:
        connected = False
    step_temperature()
    if connected:
        tp = t0 + 500 + rng.randint(-8, 8)
        send(tp, 0x10, b"", status_payload(tp))
        # occasional zero-length bulk IN (noise)
        if rng.random() < 0.08:
            packets.append((tp + 11, DEV, 0x82, "IN", "bulk", b""))
    # the mouse moves in bursts (noise on the same bus)
    if rng.random() < 0.35:
        n = rng.randint(3, 12)
        tm = t0 + rng.randint(0, 900)
        for k in range(n):
            btn = 1 if (k == n - 1 and rng.random() < 0.3) else 0
            dx, dy = rng.randint(-6, 6) & 0xFF, rng.randint(-6, 6) & 0xFF
            packets.append((tm + 8 * k, MOUSE, 0x81, "IN", "interrupt", bytes([btn, dx, dy, 0])))

packets.sort(key=lambda p: p[0])
events.sort(key=lambda e: e[0])

# ---------------------------------------------------------------- write
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
con.executescript("""
CREATE TABLE session (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE packets (
  id INTEGER PRIMARY KEY,
  t_ms INTEGER NOT NULL,          -- milliseconds since the recording started
  bus INTEGER NOT NULL,
  device INTEGER NOT NULL,        -- USB device address on the bus
  endpoint TEXT NOT NULL,         -- e.g. 0x02 (OUT) or 0x82 (IN)
  direction TEXT NOT NULL,        -- OUT = computer to device, IN = device to computer
  transfer TEXT NOT NULL,         -- control, bulk or interrupt
  length INTEGER NOT NULL,
  data_hex TEXT NOT NULL          -- payload bytes, space-separated hex
);
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  t_ms INTEGER NOT NULL,
  kind TEXT NOT NULL,             -- click, screenshot or note
  description TEXT NOT NULL       -- what the user did or saw
);
""")
con.executemany("INSERT INTO session VALUES (?, ?)", [
    ("tool", "synthetic capture in the style of a USB recorder (made for a course exercise)"),
    ("instrument", "LumoPlate 3000 absorbance plate reader (fictional)"),
    ("host", "Windows PC with the vendor app 'LumoPlate Control'"),
    ("bus", "1"),
    ("note", "Other devices on the same USB bus were recorded too."),
])
con.executemany(
    "INSERT INTO packets (t_ms, bus, device, endpoint, direction, transfer, length, data_hex) VALUES (?,?,?,?,?,?,?,?)",
    [(t, 1, d, f"0x{ep:02X}", di, tr, len(b), b.hex(" ").upper()) for t, d, ep, di, tr, b in packets])
con.executemany("INSERT INTO events (t_ms, kind, description) VALUES (?,?,?)", events)
con.commit()
con.close()

with open(EVCSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["t_ms", "kind", "description"])
    w.writerows(events)

print(f"{len(packets)} packets, {len(events)} events -> {DB}")
