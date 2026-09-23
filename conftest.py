import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.enums import Role
from app.models import User
from app.security import hash_password
from main import app

TEST_DATABASE_URL = "postgresql://postgres:123@localhost:5432/bookstore_test"

test_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    yield TestClient(app)
    app.dependency_overrides.clear()


def make_user(session, username, role, password="Password123"):
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=hash_password(password),
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def headers_for(client, username, password="Password123"):
    response = client.post("/auth/login", data={"username": username, "password": password})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(name="customer")
def customer_fixture(session, client):
    make_user(session, "amina", Role.customer)
    return headers_for(client, "amina")


@pytest.fixture(name="staff")
def staff_fixture(session, client):
    make_user(session, "karim", Role.staff)
    return headers_for(client, "karim")


@pytest.fixture(name="admin")
def admin_fixture(session, client):
    make_user(session, "owner", Role.admin)
    return headers_for(client, "owner")


@pytest.fixture(name="author")
def author_fixture(client, staff):
    return client.post("/authors", json={"name": "Frank Herbert"}, headers=staff).json()


@pytest.fixture(name="a_book")
def a_book_fixture(client, staff, author):
    return client.post(
        "/books",
        json={"title": "Dune", "author_id": author["id"], "price": 12.5, "stock": 3},
        headers=staff,
    ).json()
