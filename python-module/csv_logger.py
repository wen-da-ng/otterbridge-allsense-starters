"""Starter outside module: log phone streams to a CSV file.

Copy this folder, rename it, and change `handle()` (and the CSV parts) to do your thing. It's an
"outside module" (https://docs.allsense.otterbridge.org/MODULES/): a program that speaks the AllSense protocol through the
Python client. It shows the patterns every module needs:

- wait for the phone if it isn't up yet (`connect(wait=…)`), and ride out drops (the client
  reconnects and resubscribes by itself);
- tell the user when a stream isn't shared or is refused (`sub.state`), once, and when it's back;
- use the phone's sample time `s.t` (ns, phone boot clock) for intervals, `s.time` (Unix s) for logs.

    python csv_logger.py "<link from the app (Home → Connect)>" accelerometer gyroscope --seconds 10
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from typing import Callable, Dict, Optional, Sequence, TextIO

import allsense

PROBLEMS = {
    "not_shared": "isn't shared over the network. In the AllSense app: Home → Connect → Browser → Streams it may send → Choose.",
    "refused": "is refused by Android on this phone; pick another stream.",
}


def run(phone: "allsense.Phone", streams: Sequence[str], out: TextIO, seconds: Optional[float],
        rate: float = 50, say: Callable[[str], None] = lambda m: print(m, file=sys.stderr)) -> int:
    """Writes one row per sample: unix time, stream name, values. Returns the number of rows.

    Runs for ``seconds`` (None: until Ctrl+C). ``say`` gets messages for the user.
    """
    writer = csv.writer(out)
    writer.writerow(["time", "stream", "values"])
    subs = phone.subscribe(list(streams), rate)  # raises AllSenseError for a name the phone doesn't have
    told: Dict[str, Optional[str]] = {}
    rows = 0
    end = None if seconds is None else time.monotonic() + seconds
    try:
        while end is None or time.monotonic() < end:
            for sub in subs:
                # Tell the user once when a stream can't be received, and once when it's back.
                state = sub.state
                if state in PROBLEMS and told.get(sub.info.name) != state:
                    say(f"{sub.info.name} {PROBLEMS[state]}")
                elif state == "streaming" and told.get(sub.info.name) in PROBLEMS:
                    say(f"{sub.info.name} is streaming again.")
                told[sub.info.name] = state
                for s in sub.read(timeout=0.05):
                    rows += handle(writer, sub.info.name, s)
    except KeyboardInterrupt:
        pass
    finally:
        for sub in subs:
            sub.close()
    return rows


def handle(writer, name: str, s: "allsense.Sample") -> int:
    """Your module's logic, per sample. Returns rows written."""
    writer.writerow([f"{s.time:.6f}", name, *s.values])
    return 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("url", help="the link from the app (Home → Connect) (it contains the token)")
    ap.add_argument("streams", nargs="+", help="stream names as set in the app, e.g. accelerometer")
    ap.add_argument("--seconds", type=float, default=None, help="stop after this long (default: until Ctrl+C)")
    ap.add_argument("--out", default="allsense_log.csv")
    a = ap.parse_args(argv)
    try:
        # wait: keep trying while the phone isn't up yet (a robot often boots first).
        with allsense.connect(a.url, name="csv_logger", wait=float("inf")) as phone, open(a.out, "w", newline="") as f:
            n = run(phone, a.streams, f, a.seconds)
    except allsense.TokenError as e:
        print(f"{e}. Copy the current link from the app (Home → Connect).", file=sys.stderr)
        return 2
    except allsense.AllSenseError as e:
        print(e, file=sys.stderr)
        return 1
    print(f"Wrote {n} rows to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
