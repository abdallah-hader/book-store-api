from datetime import datetime
from pydantic import BaseModel

from app.enums import Genre, OrderStatus, Role


class UserResponse(BaseModel):
	id: int
	username: str
	email: str
	role: Role
	is_active: bool


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"

class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    genre: Genre
    price: float
    stock: int

class OrderResponse(BaseModel):
    id: int
    user_id: int
    book_title: str
    book_author: str
    book_id: int
    quantity: int
    total_price: float
    status: OrderStatus
    created_at: datetime
