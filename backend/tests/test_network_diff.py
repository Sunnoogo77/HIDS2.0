from datetime import datetime, timezone, timedelta

from app.services.network_streamer import calculate_delta


def test_calculate_delta_added_updated_removed():
    now = datetime.now(timezone.utc)
    state = {}
    last_sent = {}
    current = [
        {"key": "tcp|1:1|2:2|10", "status": "ESTABLISHED", "process_name": "p1"},
        {"key": "tcp|1:2|3:4|20", "status": "LISTEN", "process_name": "p2"},
    ]
    added, updated, removed = calculate_delta(state, last_sent, current, now)
    assert len(added) == 2
    assert updated == []
    assert removed == []

    later = now + timedelta(seconds=15)
    current2 = [
        {"key": "tcp|1:1|2:2|10", "status": "CLOSE_WAIT", "process_name": "p1"},
    ]
    added, updated, removed = calculate_delta(state, last_sent, current2, later)
    assert added == []
    assert len(updated) == 1
    assert removed == ["tcp|1:2|3:4|20"]
