# # app/api/fs.py
# from fastapi import APIRouter, Depends, HTTPException, Query
# from pydantic import BaseModel
# from typing import List, Literal
# from pathlib import Path
# import os

# router = APIRouter(prefix="/api/fs", tags=["fs"])

# # Limite les racines autorisées (à adapter)
# ALLOWED_ROOTS = [Path("/"), Path("/var"), Path("/etc"), Path("/home")]

# class FsItem(BaseModel):
#     name: str
#     path: str
#     type: Literal["dir", "file"]

# class FsListResp(BaseModel):
#     cwd: str
#     items: List[FsItem]

# def _is_allowed(p: Path) -> bool:
#     try:
#         rp = p.resolve()
#     except Exception:
#         return False
#     return any(str(rp).startswith(str(root.resolve())) for root in ALLOWED_ROOTS)

# @router.get("/list", response_model=FsListResp)
# def list_dir(
#     path: str = Query("/", description="Chemin absolu à lister"),
#     kind: Literal["any", "dir", "file"] = Query("any")
# ):
#     p = Path(path).expanduser()
#     if not p.is_absolute():
#         raise HTTPException(400, "Absolute path required")
#     if not _is_allowed(p):
#         raise HTTPException(403, "Path not allowed")
#     if not p.exists():
#         raise HTTPException(404, "Path not found")

#     target = p if p.is_dir() else p.parent
#     items: List[FsItem] = []
#     try:
#         for entry in sorted(target.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
#             t = "dir" if entry.is_dir() else "file"
#             if kind != "any" and t != kind:
#                 continue
#             items.append(FsItem(name=entry.name, path=str(entry), type=t))
#     except PermissionError:
#         raise HTTPException(403, "Permission denied")

#     return FsListResp(cwd=str(target), items=items)

# app/api/fs.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Literal
from pathlib import Path
from pydantic import BaseModel

# si tu veux protéger la route par auth, décommente et adapte :
# from app.core.security import get_current_user

router = APIRouter(prefix="/api/fs", tags=["filesystem"])

class FsItem(BaseModel):
    name: str
    path: str
    type: Literal["file", "dir"]

class FsListResponse(BaseModel):
    cwd: str
    items: list[FsItem]

# Optionnel: limite la navigation à ces racines (sécurité)
ALLOWED_ROOTS: list[Path] = [Path("/")]  # ajoute /data, /var, etc. si besoin

def _is_under_allowed_roots(p: Path) -> bool:
    try:
        r = p.resolve()
    except FileNotFoundError:
        # autorise la résolution même si le dossier n'existe pas encore
        r = p
    for root in ALLOWED_ROOTS:
        try:
            if r == root.resolve() or root.resolve() in r.parents:
                return True
        except FileNotFoundError:
            pass
    return False

@router.get("/list", response_model=FsListResponse)
def list_entries(
    path: str = Query("/", description="Chemin absolu sur le serveur"),
    kind: Literal["any", "file", "dir"] = Query("any")
    # , user=Depends(get_current_user)  # si tu sécurises
):
    p = Path(path).expanduser()
    if not p.is_absolute():
        raise HTTPException(status_code=400, detail="Path must be absolute")

    if not _is_under_allowed_roots(p):
        raise HTTPException(status_code=403, detail="Path not allowed")

    # Si le chemin demandé est un fichier, on liste son dossier parent
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
