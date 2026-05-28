from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.core.security import get_password_hash

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

SyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


def get_db_session():
    """Create a new sync database session."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_sync_db_session():
    """Synchronous database session for tests."""
    session = SyncSessionLocal()
    try:
        yield session
    finally:
        session.close()


def init_db(session) -> None:
    """Initialize database - creates superuser if it doesn't exist (sync version)."""
    from app.models import User, UserCreate, UserScope
    from app.config import settings as app_settings

    statement = select(User).where(User.email == app_settings.FIRST_SUPERUSER)
    user_result = session.execute(statement)
    user = user_result.scalar()
    if user is None:
        user_in = UserCreate(
            email=app_settings.FIRST_SUPERUSER,
            password=app_settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        db_user = User.model_validate(
            user_in, update={"hashed_password": get_password_hash(user_in.password)}
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        session.add(UserScope(user_id=db_user.id, scope="superuser"))
        session.commit()
