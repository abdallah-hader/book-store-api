from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_db_session
from app.dependencies import get_current_user, require_roles
from app.dtos.requests import OrderCreateRequest, OrderStatusUpdateRequest
from app.dtos.responces import OrderResponse
from app.enums import OrderStatus, Role
from app.models import Book, Order, User

router = APIRouter(prefix="/orders", tags=["orders"])

STAFF_ROLES = [Role.staff, Role.admin]
staff_or_admin = require_roles(STAFF_ROLES)


@router.post("", response_model=OrderResponse, status_code=201)
def place_order(
    new_order: OrderCreateRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    book = session.get(Book, new_order.book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not exists")
    if book.stock < new_order.quantity:
        raise HTTPException(status_code=409, detail=f"Only {book.stock} left in stock")

    book.stock -= new_order.quantity
    order = Order(
        user_id=current_user.id,
        book_id=book.id,
        quantity=new_order.quantity,
        total_price=round(book.price * new_order.quantity, 2),
    )
    session.add(book)
    session.add(order)
    session.commit()
    session.refresh(order)
    return OrderResponse(
    id=order.id,
    user_id=order.user_id,
    book_title=book.title,
    book_author=book.author,
    book_id=order.book_id,
    quantity=order.quantity,
    total_price=order.total_price,
    status=order.status,
    created_at=order.created_at,
)

@router.get("", response_model=list[OrderResponse])
def list_orders(
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    query = select(Order)
    if current_user.role not in STAFF_ROLES:
        query = query.where(Order.user_id == current_user.id)

    orders = session.exec(query).all()
    result = []

    for order in orders:
        book = session.get(Book, order.book_id)

        result.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                book_title=book.title,
                book_author=book.author,
                book_id=order.book_id,
                quantity=order.quantity,
                total_price=order.total_price,
                status=order.status,
                created_at=order.created_at,
            )
        )

    return result

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user.id and current_user.role not in STAFF_ROLES:
        raise HTTPException(status_code=404, detail="Order not found")

    book = session.get(Book, order.book_id)

    return OrderResponse(
    id=order.id,
    user_id=order.user_id,
    book_title=book.title,
    book_author=book.author,
    book_id=order.book_id,
    quantity=order.quantity,
    total_price=order.total_price,
    status=order.status,
    created_at=order.created_at,
)



@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    update: OrderStatusUpdateRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(staff_or_admin),
):
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="A cancelled order cannot be changed")

    book = session.get(Book, order.book_id)

    if update.status == OrderStatus.cancelled:
        if book is not None:
            book.stock += order.quantity
            session.add(book)

    order.status = update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return OrderResponse(
    id=order.id,
    user_id=order.user_id,
    book_title=book.title,
    book_author=book.author,
    book_id=order.book_id,
    quantity=order.quantity,
    total_price=order.total_price,
    status=order.status,
    created_at=order.created_at,
)

