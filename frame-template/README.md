# Frame template starter

`example.json` makes the phone send 16-byte frames (`AA 55`, accelerometer and gyroscope as int16, a counter, an XOR checksum) 100 times a second. Change it to match your board's protocol. Format: [Frame templates](https://docs.allsense.otterbridge.org/TEMPLATES/).

- Check: `allsense-template check example.json` (prints a byte map of an example frame: compare it with your board's protocol)
- Board on a PC port: `allsense-fake-template --port <port> --template example.json` (`COM3`, `/dev/ttyUSB0`…)
- On the phone: Home → Connect → Microcontroller, on the USB board: Speaks → Change → Import template…
