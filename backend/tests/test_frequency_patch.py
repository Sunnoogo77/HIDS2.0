from uuid import uuid4

from app.db.session import SessionLocal, commit_with_retry
from app.db.models import MonitoredFile


def test_patch_file_frequency(client):
    db = SessionLocal()
    item = MonitoredFile(
        path=f"/tmp/testfile-{uuid4().hex}",
        frequency="hourly",
        status="active",
    )
    db.add(item)
    commit_with_retry(db)
    db.refresh(item)
    db.close()

    res = client.patch(f"/api/monitoring/files/{item.id}/frequency", json={"frequency": "daily"})
    assert res.status_code == 200
    data = res.json()
    assert data["frequency"] == "daily"
