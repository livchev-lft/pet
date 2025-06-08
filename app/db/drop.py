from sqlalchemy import create_engine, MetaData
from models import Base  # Импортируйте ваши модели

DATABASE_URL = "postgresql+psycopg2://postgres:123@localhost:5432/autodb"
engine = create_engine(DATABASE_URL)

def drop_all_tables():
    # Удаляем все таблицы
    Base.metadata.drop_all(bind=engine)
    print("Все таблицы успешно удалены")

if __name__ == "__main__":
    drop_all_tables()