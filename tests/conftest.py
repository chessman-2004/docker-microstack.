import os
import pytest

# 1. FORCE SQLite environment variable BEFORE any app modules are imported
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# 2. Import database components AFTER setting environment variable
import database
from database import Base
from main import app, get_db

# 3. Create a shared in-memory SQLite engine
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Rebind database sessionmaker globally
database.engine = test_engine
database.SessionLocal = TestingSessionLocal

@pytest.fixture(scope="function", autouse=True)
def setup_db(mocker):
    """Prepares SQLite tables and ensures tasks.py uses TestingSessionLocal."""
    Base.metadata.create_all(bind=test_engine)
    
    # Patch tasks module to guarantee it never uses the un-mocked PostgreSQL engine
    mocker.patch("tasks.SessionLocal", TestingSessionLocal)
    
    yield
    Base.metadata.drop_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db