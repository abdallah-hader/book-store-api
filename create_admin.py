"""cli script that creates the first admin account."""

from getpass import getpass

from pydantic import ValidationError
from sqlmodel import Session, select

from app.database import create_db_and_tables, engine
from app.dtos.requests import UserCreateRequest
from app.enums import Role
from app.models import User
from app.security import hash_password


def create_admin(username: str, email: str, password: str):
    details = UserCreateRequest(username=username, email=email, password=password)

    with Session(engine) as session:
        taken = session.exec(
            select(User).where((User.username == details.username) | (User.email == details.email))
        ).first()
        if taken:
            raise ValueError("A user with that username or email already exists")

        admin = User(
            username=details.username,
            email=details.email,
            hashed_password=hash_password(details.password),
            role=Role.admin,
        )
        session.add(admin)
        session.commit()
        session.refresh(admin)
        return admin


if __name__ == "__main__":
    create_db_and_tables()

    entered_username = input("Admin username: ")
    entered_email = input("Admin email: ")
    entered_password = getpass("Admin password: ")

    try:
        new_admin = create_admin(entered_username, entered_email, entered_password)
    except ValidationError as error:
        print("Could not create admin:")
        for problem in error.errors():
            print(f"  {problem['loc'][0]}: {problem['msg']}")
    except ValueError as error:
        print(f"Could not create admin: {error}")
    else:
        print(f"Created admin '{new_admin.username}' with id {new_admin.id}")
