# AllSense starters

Starting points for building on **AllSense by OtterBridge**, the app that turns an Android phone into a sensor hub for robots. Copy a folder, change it, and test it on your PC without a phone.

| Folder | What you build | Check it with |
|---|---|---|
| [`frame-template/`](frame-template) | A **frame template**: a JSON file that makes the phone send frames in your board's own serial protocol. No code | `allsense-template check frame-template/example.json` |
| [`python-module/`](python-module) | An **outside module** in Python: a program that reads the phone's streams (this one logs them to CSV) | `pytest -q python-module` |
| [`skills/allsense-module/`](skills/allsense-module/SKILL.md) | A step-by-step guide for a person or an AI agent: pick the kind, start from a starter, test, hand off | |

Which kind to pick, and the rules every module follows: [Modules](https://docs.allsense.otterbridge.org/MODULES/) on the docs site.

## Setup

```bash
pip install "allsense-testkit[all] @ git+https://github.com/wen-da-ng/otterbridge-allsense-protocol"   # fake phones + template checker
pip install "allsense @ git+https://github.com/wen-da-ng/otterbridge-allsense-python"                 # the Python client
```

(Both will be on PyPI as `allsense-testkit` and `allsense`.)

The test kit gives you stand-in phones, so you can test before touching the real one: `allsense-fake-phone` for programs, `allsense-fake-serial` / `allsense-fake-ble` for boards, `allsense-fake-template` for frame-template boards.

## Related

- [otterbridge-allsense-protocol](https://github.com/wen-da-ng/otterbridge-allsense-protocol): the protocol spec and the test kit
- Clients: [Python](https://github.com/wen-da-ng/otterbridge-allsense-python), [C++](https://github.com/wen-da-ng/otterbridge-allsense-cpp), [Rust](https://github.com/wen-da-ng/otterbridge-allsense-rust), [ROS 2](https://github.com/wen-da-ng/otterbridge-allsense-ros2), [Arduino/ESP32](https://github.com/wen-da-ng/otterbridge-allsense-arduino)
- Docs: https://docs.allsense.otterbridge.org/

## Licence

MIT. What you build from these is yours, under any licence.
