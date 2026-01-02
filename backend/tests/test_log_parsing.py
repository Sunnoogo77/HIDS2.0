from app.core.log_parsing import extract_json_payload, classify_scan_event


def test_extract_json_payload_from_prefixed_line():
    line = "2025-01-01 00:00:00,000 | INFO | hids | {\"type\": \"activity\", \"activity_type\": \"file_unchanged\"}"
    data = extract_json_payload(line)
    assert data is not None
    assert data["type"] == "activity"
    assert data["activity_type"] == "file_unchanged"


def test_classify_scan_event():
    assert classify_scan_event({"activity_type": "folder_modified"}) == "folder_scan"
    assert classify_scan_event({"activity_type": "ip_baseline_established"}) == "ip_scan"
