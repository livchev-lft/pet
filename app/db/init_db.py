from sqlalchemy import create_engine
from models import Base

DATABASE_URL = "postgresql+psycopg2://postgres:123@localhost:5432/autodb"
print(list(DATABASE_URL.encode('utf-8')))
print(DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=True)

def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
