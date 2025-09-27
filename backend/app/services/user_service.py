# File: backend/app/services/user_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User as ORMUser
from app.models.user import UserCreate
from app.services.auth_service import get_password_hash


def get_users() -> List[ORMUser]:
    db: Session = SessionLocal()
    users = db.query(ORMUser).all()
    db.close()
    return users


def get_user(user_id: int) -> Optional[ORMUser]:
    db: Session = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
    db.close()
    return user


def create_user(user_in: UserCreate) -> ORMUser:
    db: Session = SessionLocal()
    # Vérifier qu’aucun user n’existe déjà avec ce mail ou username
    if db.query(ORMUser).filter(ORMUser.email == user_in.email).first():
        db.close()
        raise ValueError("Email already registered")
    if db.query(ORMUser).filter(ORMUser.username == user_in.username).first():
        db.close()
        raise ValueError("Username already taken")

    db_user = ORMUser(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        is_admin=user_in.is_admin,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user


def update_user(user_id: int, user_in: UserCreate) -> Optional[ORMUser]:
    db: Session = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
    if not user:
        db.close()
        return None
    # Met à jour email, username, statut admin
    user.username = user_in.username
    user.email = user_in.email
    user.is_admin = user_in.is_admin
    db.commit()
    db.refresh(user)
    db.close()
    return user


def delete_user(user_id: int) -> bool:
    db: Session = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
    if not user:
        db.close()
        return False
    db.delete(user)
    db.commit()
    db.close()
    return True


def change_user_password(user_id: int, new_password: str) -> bool:
    db: Session = SessionLocal()
    user = db.query(ORMUser).filter(ORMUser.id == user_id).first()
    if not user:
        db.close()
        return False
    user.password_hash = get_password_hash(new_password)
    db.commit()
    db.close()
    return True