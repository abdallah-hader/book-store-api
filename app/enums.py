from enum import Enum

class Role(str, Enum):
	customer = "customer"
	staff = "staff"
	admin = "admin"

class Genre(str, Enum):
	fiction = "fiction"
	nonfinction = "nonfiction"
	poetry = "poetry"

class OrderStatus(str, Enum):
	pending = "pending"
	shipped = "shipped"
	cancelled = "cancelled"