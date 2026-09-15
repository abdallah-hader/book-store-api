from sqlmodel import SQLModel, Session, create_engine
from app.config import settings

engine = create_engine(
settings.database_url,
echo=settings.debug,
connect_args={"check_same_thread": False},
)

def create_db_and_tables():
	SQLModel.metadata.create_all(engine)


def get_db_session():
	with Session(engine) as s:
		yield s