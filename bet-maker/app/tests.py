import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# SQLite temp database
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

client = TestClient(app)

@pytest.fixture(scope="module")
async def db_setup():
    """Set up the test database and create tables"""
    print("setup db")  
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("tables created")

    yield 
    
    # Drop db
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def event_data():
    return {
        "coef": 2.5,
        "deadline": "2024-10-18T15:30:00"
    }

@pytest.mark.asyncio
async def test_create_event(event_data, db_setup):
    """Test create_event endpoint."""
    response = client.post("/events/", json=event_data)
    print(f"Response: {response.json()}")

    assert response.status_code == 200
    assert "coef" in response.json()

@pytest.mark.asyncio
async def test_create_event_invalid_data(db_setup):
    """Send invalid data."""
    invalid_event_data = {
        "coef": -1.5,
        "deadline": "12-31-2024T23:59:59Z"
    }

    response = client.post("/events/", json=invalid_event_data)
    print(f"Invalid Response: {response.json()}") 

    assert response.status_code == 422
