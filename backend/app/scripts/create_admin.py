import argparse
import os
import sys
from pathlib import Path


def _bootstrap_paths() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    backend_dir = repo_root / "backend"
    sys.path.insert(0, str(backend_dir))


def _ensure_jwt_secret() -> None:
    if not os.getenv("JWT_SECRET"):
        os.environ["JWT_SECRET"] = "dev-secret"
        print("WARN: JWT_SECRET not set; using temporary dev-secret for this script.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or update an admin user in SQLite.")
    parser.add_argument("--username", required=True, help="Username to create/update.")
    parser.add_argument("--password", help="Password for new user or reset.")
    parser.add_argument("--email", help="Email address (default: <username>@local).")
    parser.add_argument("--admin", dest="is_admin", action="store_true", default=True)
    parser.add_argument("--no-admin", dest="is_admin", action="store_false")
    parser.add_argument("--reset-password", action="store_true", help="Reset password if user exists.")
    parser.add_argument("--make-admin", action="store_true", help="Force admin flag if user exists.")
    return parser.parse_args()


def main() -> int:
    _bootstrap_paths()
    _ensure_jwt_secret()

    from app.db.session import SessionLocal, commit_with_retry
    from app.db.models import User as ORMUser
    from app.services.auth_service import get_password_hash

    args = parse_args()
    username = args.username.strip()
    email = (args.email or f"{username}@local").strip()

    if not username:
        print("ERROR: username is required.")
        return 2

    db = SessionLocal()
    try:
        user = db.query(ORMUser).filter(ORMUser.username == username).first()
        if user:
            print(f"INFO: user '{username}' already exists (id={user.id}).")
            if not args.reset_password and not args.make_admin:
                print("No action taken. Re-run with --reset-password and/or --make-admin.")
                return 0

            changed = False
            if args.reset_password:
                if not args.password:
                    print("ERROR: --reset-password requires --password.")
                    return 2
                user.password_hash = get_password_hash(args.password)
                changed = True
                print("OK: password updated.")

            if args.make_admin and not user.is_admin:
                user.is_admin = True
                changed = True
                print("OK: admin flag enabled.")

            if changed:
                commit_with_retry(db)
            return 0

        if db.query(ORMUser).filter(ORMUser.email == email).first():
            print(f"ERROR: email '{email}' already exists.")
            return 2

        if not args.password:
            print("ERROR: --password is required when creating a user.")
            return 2

        new_user = ORMUser(
            username=username,
            email=email,
            password_hash=get_password_hash(args.password),
            is_admin=args.is_admin,
            is_active=True,
        )
        db.add(new_user)
        commit_with_retry(db)
        db.refresh(new_user)

        print("OK: user created.")
        print(f"  username: {username}")
        print(f"  email:    {email}")
        print(f"  admin:    {new_user.is_admin}")
        print(f"  password: {args.password}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
