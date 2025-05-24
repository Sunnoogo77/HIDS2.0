from app.db.session import SessionLocal
from app.db.models import User as ORMUser
from app.models.user import UserCreate
from app.services.auth_service import get_password_hash

def create_user(user_in: UserCreate) -> ORMUser:
    db = SessionLocal()
    # Vérifier qu’aucun user n’existe déjà avec ce mail
    if db.query(ORMUser).filter(ORMUser.email == user_in.email).first():
        db.close()
        raise ValueError("Email already registered")

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
