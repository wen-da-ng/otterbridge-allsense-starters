---
name: allsense-module
description: Build a module for OtterBridge AllSense, the app that turns an Android phone into a sensor hub for robots. Use when someone wants to connect a board, program or robot to AllSense - a frame template for a board with its own protocol, or an outside program or firmware that speaks the AllSense protocol (logger, bridge, dashboard, board library). Covers picking the kind, starting from a starter, testing without the phone, and the done checklist.
---

# Build an AllSense module

AllSense is a hub: the phone streams its sensors, and anything that speaks the AllSense protocol can use them. You are building one of those things. The starters are in https://github.com/wen-da-ng/otterbridge-allsense-starters; the protocol and its test kit (fake phones, template checker) in https://github.com/wen-da-ng/otterbridge-allsense-protocol.

Read first, in this order: [Modules](https://docs.allsense.otterbridge.org/MODULES/) (the contract), then the spec for your kind ([Frame templates](https://docs.allsense.otterbridge.org/TEMPLATES/) or [Protocol](https://docs.allsense.otterbridge.org/PROTOCOL/)). Each docs page is also plain Markdown: add `index.md` to its URL, or read https://docs.allsense.otterbridge.org/llms-full.txt.

Setup on the PC: `pip install "allsense-testkit[all] @ git+https://github.com/wen-da-ng/otterbridge-allsense-protocol" "allsense @ git+https://github.com/wen-da-ng/otterbridge-allsense-python"` (soon on PyPI as `allsense-testkit` and `allsense`).

## 1. Pick the kind

Ask, in order, and take the first yes:

1. **Does the board already have its own serial protocol that shouldn't change?** → **Frame template** (a JSON file, no code). Go to §2.
2. **Does it run off the phone** (PC, robot computer, browser, microcontroller)? → **Outside module**. Go to §3.
3. **Does it need a new way for clients to reach the phone** that the phone itself must drive (a radio or network protocol the app doesn't speak yet)? → That needs a change inside the app, which is closed source. First check whether an outside module can bridge it (a program on a PC or board that speaks the AllSense protocol on one side and the new protocol on the other). If not, open an issue at https://github.com/wen-da-ng/otterbridge-allsense/issues describing the use.

If the person isn't sure, ask what device it runs on and what it should do with the data. Outside modules need no app change and can use any language.

## 2. Frame template

1. Copy `frame-template/example.json` from the starters. Change `name` (a–z, 0–9, `_`) and replace `description`.
2. Fill `fields` from the board's protocol: header bytes, then each value's stream, index, type, scale; a counter; the checksum. Ask for the board's protocol document or its parsing code if you don't have it; don't guess byte orders or checksums.
   - Stream names, their values and **units** (gyroscope is rad/s, pressure hPa…) are in [Frame templates](https://docs.allsense.otterbridge.org/TEMPLATES/) "Stream names and units". Put unit conversions in `scale` (any real number; negative flips an axis).
   - Ask how the phone is mounted if the board expects robot axes (pitch, roll…): Android's axes are in the same section. Remap with `idx`.
3. Check it: `allsense-template check path/to/file.json`. Fix every FAIL. It prints a byte map of an example frame: compare it with the board's expected layout byte by byte, and check endian, checksum and baud on its second line.
4. If the board is on a PC serial port: `allsense-fake-template --port <COM> --template <file>` (a BLE board: `--ble "<name>"` instead of `--port`). If you can change the board's firmware, make it print `frames=<good> bad=<bad>` once a second (see the Arduino library's `examples/TemplateReader`, https://github.com/wen-da-ng/otterbridge-allsense-arduino): the tool then says PASS or FAIL. If you can't, it says "SENT, not verified": then confirm with the board's own behaviour.
5. Wiring, if the board has only UART pins: a USB-UART adapter (CH340, CP210x, FTDI, PL2303) on the phone's USB port, adapter TX → board RX, GND → GND, matching logic level (3.3 V / 5 V). Details: [Frame templates](https://docs.allsense.otterbridge.org/TEMPLATES/) "Connecting the board".
6. Hand-off for the phone (fill in the brackets):
   > Copy `<file>.json` to the phone. Plug `<board>` into the phone's USB port. In AllSense: Home → Connect → Microcontroller, on the USB board: Speaks → Change → Import template…, pick `<file>.json`, then select `<name>`. Tap Start streaming. You should see `<what the board does>`.
   >
   > (BLE board: Start streaming, then Connect → Microcontroller → By Bluetooth → `<board>` "Nearby · its own protocol" → Connect… → Import template… → select `<name>`.)

## 3. Outside module

1. Pick the protocol by where it runs (table in [Modules](https://docs.allsense.otterbridge.org/MODULES/)): JSON over WebSocket for computers, compact binary over USB or BLE for microcontrollers.
2. Start from the closest starter:
   - Python: copy `python-module/` from the starters (a CSV logger and its tests: unknown stream, not shared, phone drops). It shows the patterns the rules below need. Its tests use the test kit's `FakePhone`.
   - Arduino/ESP32: copy an example from the Arduino library's `examples/` (https://github.com/wen-da-ng/otterbridge-allsense-arduino: `USBQuickstart`, `BLEQuickstart`, `WiFiQuickstart`).
   - C++, Rust or ROS 2: start from that client's examples (https://github.com/wen-da-ng/otterbridge-allsense-cpp, https://github.com/wen-da-ng/otterbridge-allsense-rust, https://github.com/wen-da-ng/otterbridge-allsense-ros2).
   - Another language: implement from the [Protocol](https://docs.allsense.otterbridge.org/PROTOCOL/) spec. Use the shared vectors in the protocol repo (`vectors/`) as tests, and run the shared scenarios with `allsense-conformance -- <your test program>`.
3. Follow the rules in [Modules](https://docs.allsense.otterbridge.org/MODULES/): look streams up by name, handle `refused` and `not_shared`, reconnect and resubscribe, use sample timestamps.
4. Test against a fake phone (table in [Modules](https://docs.allsense.otterbridge.org/MODULES/), including how to make it unshare a stream, send chosen values, go silent or restart). For Python: `pytest -q <your folder>`. Write tests for: receiving samples, an unknown stream, a `not_shared` stream that's shared later, and the phone dropping and coming back.
5. Hand-off for the phone (fill in the brackets):
   > In AllSense: Home → Start streaming. Copy the link from Connect → Browser (same Wi-Fi as `<computer>`). Run `<command with "<link>">`. You should see `<output>`. If it says a stream isn't shared: Connect → Browser → Streams it may send → Choose.

## Done checklist

- [ ] The kind fits (§1), and the module only uses the documented API or spec.
- [ ] Every check for its kind passes on a PC (`allsense-template check` / fake phone tests).
- [ ] Code modules: it handles a stream it can't get (unknown, `refused`, `not_shared`) with a clear message, not a crash or silence. (Templates: the app shows this for you.)
- [ ] Code modules: it survives the link dropping (cable out, Wi-Fi gone, streaming stopped) and recovers when it's back. (Templates: the phone reconnects for you; the board just sees frames stop and start.)
- [ ] A short README next to it: what it does, how to run it, how to test it. For a template, a few lines saying which board and protocol it's for.
- [ ] The hand-off steps for the phone, filled in.
- [ ] If it needs a protocol change: stop. Protocol changes go through the protocol repo first (spec, vectors, test kit), then the app and every client: open an issue at https://github.com/wen-da-ng/otterbridge-allsense-protocol/issues.

## Gotchas

- USB to an ESP32: DTR on, RTS off. RTS alone resets the chip.
- ESP32-S3 `Serial` goes over USB only with "USB CDC On Boot: Enabled".
- A board on the phone's USB port can't also be on your PC: test it on the PC first (fake phone), then move it.
- BLE scans find nothing while the phone's Location is off.
- The phone's catalog is about 18 KB; small boards on Wi-Fi connect with `&catalog=none`.
