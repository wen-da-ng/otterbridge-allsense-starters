"""Runs the module against the fake phone: no phone needed.

    pytest -q                      (from this folder, with allsense and allsense-testkit installed)

The fake phone is FakePhone from the test kit (pip install allsense-testkit). What a test can make
it do: set_shared(name, False/True), set_values(name, fn), frozen.set()/clear(), stop()/restart().
"""

import io
import os
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import allsense  # noqa: E402
from allsense_testkit import FakePhone  # noqa: E402
from csv_logger import run  # noqa: E402


@pytest.fixture
def server():
    s = FakePhone()
    yield s
    s.stop()


@pytest.fixture
def phone(server):
    with allsense.connect(server.url, name="test", stall_timeout=2) as p:
        yield p


def test_logs_rows_for_each_stream(phone):
    out = io.StringIO()
    rows = run(phone, ["accelerometer", "gyroscope"], out, seconds=1.0, rate=50)
    lines = out.getvalue().splitlines()
    assert lines[0] == "time,stream,values"
    assert {line.split(",")[1] for line in lines[1:]} == {"accelerometer", "gyroscope"}
    assert rows >= 60  # ~100 expected at 2 × 50 Hz; generous for slow PCs


def test_unknown_stream_is_explained(phone):
    with pytest.raises(allsense.AllSenseError, match="No stream called"):
        run(phone, ["no_such_sensor"], io.StringIO(), seconds=0.1)


def test_not_shared_is_explained_and_recovers(phone, server):
    server.set_shared("accelerometer", False)
    messages = []
    # The user shares it again after 1 s, in the app.
    threading.Timer(1.0, server.set_shared, args=("accelerometer", True)).start()
    rows = run(phone, ["accelerometer"], io.StringIO(), seconds=2.0, say=messages.append)
    assert any("isn't shared" in m for m in messages)
    assert any("streaming again" in m for m in messages)
    assert rows > 0


def test_keeps_going_when_the_phone_drops(phone, server):
    def drop_and_return():
        server.stop()
        time.sleep(1.0)
        server.restart()

    threading.Timer(0.5, drop_and_return).start()
    out = io.StringIO()
    run(phone, ["accelerometer"], out, seconds=6.0)
    late = [line for line in out.getvalue().splitlines()[1:] if float(line.split(",")[0]) > time.time() - 2]
    assert late, "no samples after the phone came back"
