import os
import sys
import time
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.models import AdminRole, AdminUser, AdminUserRole  # noqa: E402
from app.services.admin_service import hash_admin_password  # noqa: E402


def normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def ensure_role(db: Session, code: str, name: str, now: int) -> AdminRole:
    role = db.scalars(select(AdminRole).where(AdminRole.code == code).limit(1)).first()
    if role is not None:
        return role
    role = AdminRole(code=code, name=name, created_at=now)
    db.add(role)
    db.flush()
    return role


def ensure_admin_user(db: Session, username: str, password: str, display_name: str, now: int) -> AdminUser:
    user = db.scalars(select(AdminUser).where(AdminUser.username == username).limit(1)).first()
    password_hash = hash_admin_password(password)
    if user is not None:
        user.password_hash = password_hash
        user.display_name = display_name
        user.status = "active"
        user.updated_at = now
        db.flush()
        return user
    user = AdminUser(
        username=username,
        password_hash=password_hash,
        display_name=display_name,
        status="active",
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    return user


def ensure_user_role(db: Session, admin_user_id, admin_role_id, now: int) -> None:
    existing = db.scalars(
        select(AdminUserRole)
        .where(AdminUserRole.admin_user_id == admin_user_id)
        .where(AdminUserRole.admin_role_id == admin_role_id)
        .limit(1)
    ).first()
    if existing is not None:
        return
    db.add(
        AdminUserRole(
            admin_user_id=admin_user_id,
            admin_role_id=admin_role_id,
            created_at=now,
        )
    )
    db.flush()


def main() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise SystemExit("DATABASE_URL is required")

    username = os.getenv("ADMIN_INIT_USERNAME", "admin")
    password = os.getenv("ADMIN_INIT_PASSWORD", "admin123456")
    display_name = os.getenv("ADMIN_INIT_DISPLAY_NAME", "Super Admin")

    engine = create_engine(normalize_database_url(database_url), pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    now = int(time.time())

    with SessionLocal() as db:
        super_admin_role = ensure_role(db, "super_admin", "Super Admin", now)
        ensure_role(db, "editor", "Editor", now)
        ensure_role(db, "operator", "Operator", now)

        admin_user = ensure_admin_user(db, username, password, display_name, now)
        ensure_user_role(db, admin_user.id, super_admin_role.id, now)
        db.commit()

    print("Admin seed ready")
    print(f"username={username}")
    print(f"display_name={display_name}")
    print("roles=super_admin")


if __name__ == "__main__":
    main()
