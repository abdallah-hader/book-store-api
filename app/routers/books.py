from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_db_session
from app.dependencies import require_roles
from app.dtos.requests import BookCreateRequest, BookUpdateRequest
from app.dtos.responces import BookResponse
from app.enums import Genre, Role
from app.models import Book, Order, User

router = APIRouter(prefix="/books", tags=["books"])

staff_or_admin = require_roles([Role.staff, Role.admin])
admin_only = require_roles([Role.admin])


def get_book_or_404(session, book_id):
    book = session.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.get("/", response_model=list[BookResponse])
def list_books(
    genre: Genre | None = None,
    in_stock: bool = False,
    session: Session = Depends(get_db_session),
):
    query = select(Book)
    if genre is not None:
        query = query.where(Book.genre == genre)
    if in_stock:
        query = query.where(Book.stock > 0)
    return session.exec(query).all()


@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, session: Session = Depends(get_db_session)):
    return get_book_or_404(session, book_id)


@router.post("", response_model=BookResponse, status_code=201)
def create_book(
    new_book: BookCreateRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(staff_or_admin),
):
    book = Book.model_validate(new_book.model_dump())
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.patch("/{book_id}", response_model=BookResponse)
def update_book(
    book_id: int,
    update: BookUpdateRequest,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(staff_or_admin),
):
    book = get_book_or_404(session, book_id)
    changes = update.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in changes.items():
        setattr(book, field, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(
    book_id: int,
    session: Session = Depends(get_db_session),
    current_user: User = Depends(admin_only),
):
    book = get_book_or_404(session, book_id)
    if session.exec(select(Order).where(Order.book_id == book_id)).first():
        raise HTTPException(
            status_code=409,
            detail="This book has orders. Set its stock to 0 instead of deleting it.",
        )
    session.delete(book)
    session.commit()

