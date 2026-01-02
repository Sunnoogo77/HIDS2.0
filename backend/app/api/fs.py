from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal
from pathlib import Path
from pydantic import BaseModel

from app.core.config import settings
from app.core.security import get_current_active_user


def _require_admin(user=Depends(get_current_active_user)):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user


router = APIRouter(
    prefix="/api/fs",
    tags=["filesystem"],
    dependencies=[Depends(_require_admin)],
)


class FsItem(BaseModel):
    name: str
    path: str
    type: Literal["file", "dir"]


class FsListResponse(BaseModel):
    cwd: str
    items: list[FsItem]


def _parse_allowlist(raw: str) -> list[Path]:
    if not raw:
        return []
    items = [p.strip() for p in raw.split(",") if p.strip()]
    return [Path(p).expanduser() for p in items]


# Limite la navigation a ces racines (configurable via FS_ALLOWLIST)
ALLOWED_ROOTS: list[Path] = _parse_allowlist(settings.FS_ALLOWLIST)


def _is_under_allowed_roots(p: Path) -> bool:
    if not ALLOWED_ROOTS:
        return False
    r = p.resolve(strict=False)
    for root in ALLOWED_ROOTS:
        rr = root.resolve(strict=False)
        if r == rr or rr in r.parents:
            return True
    return False


@router.get("/list", response_model=FsListResponse)
def list_entries(
    path: str = Query("/", description="Chemin absolu sur le serveur"),
    kind: Literal["any", "file", "dir"] = Query("any")
):
    p = Path(path).expanduser()
    if not p.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute")

    if not _is_under_allowed_roots(p):
        raise HTTPException(status_code=403, detail="Path not allowed or FS allowlist not configured")

    # Si le chemin demande est un fichier, on liste son dossier parent
    if p.is_file():
        p = p.parent

    if not p.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    try:
        items: list[FsItem] = []
        for entry in sorted(p.iterdir(), key=lambda e: (not e.is_dir(), e.name.lower())):
            t = "dir" if entry.is_dir() else "file"
            if kind != "any" and t != kind:
                continue
            items.append(FsItem(name=entry.name, path=str(entry), type=t))
        return FsListResponse(cwd=str(p.resolve()), items=items)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Permission denied")
