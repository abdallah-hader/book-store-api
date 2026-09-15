from pydantic import EmailStr, Field, field_validator, BaseModel

from app.enums import Role, Genre, OrderStatus


class UserCreateRequest(BaseModel):
	username:str = Field(min_length=3, max_length=30)
	email: EmailStr
	password:str = Field(min_length=8, max_length = 128)

	@field_validator("username")
	@classmethod
	def check_user_name(cls, value):
		if not value.replace("_", "").isalnum():
			raise ValueError("it's only allowed to use charecters, numbers, and underscores")
		return value.lower()

	@field_validator("email")
	@classmethod
	def email_is_lower(cls, value):
		return value.lower()

	@field_validator("password")
	@classmethod
	def password_has_letter_and_number(cls, value):
		has_letter = any(char.isalpha() for char in value)
		has_number = any(char.isdigit() for char in value)
		if not (has_letter and has_number):
			raise ValueError("must contain at least one letter and one number")
		return value


class RoleUpdateRequest(BaseModel):
	role: Role


class ActiveUpdateRequest(BaseModel):
	is_active: bool

class BookCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    genre: Genre = Genre.fiction
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)

    @field_validator("title", "author")
    @classmethod
    def not_blank(cls, value):
        if not value.strip():
            raise ValueError("cannot be blank")
        return value.strip()


class BookUpdateRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    genre: Genre | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)

    @field_validator("title", "author")
    @classmethod
    def not_blank(cls, value):
        if value is None:
            return value
        if not value.strip():
            raise ValueError("cannot be blank")
        return value.strip()

class OrderCreateRequest(BaseModel):
    book_id: int
    quantity: int = Field(default=1, ge=1, le=10)


class OrderStatusUpdateRequest(BaseModel):
    status: OrderStatus
