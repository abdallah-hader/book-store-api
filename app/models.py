from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.enums import Genre, OrderStatus, Role


class User(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: Role = Role.customer
    is_active: bool = True


class Book(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
    genre: Genre = Genre.fiction
    price: float
    stock: int = 0


class Order(SQLModel, table=True):
    __table_args__ = {"sqlite_autoincrement": True}

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    book_id: int = Field(foreign_key="book.id", index=True)
    quantity: int
    total_price: float
    status: OrderStatus = OrderStatus.pending
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
