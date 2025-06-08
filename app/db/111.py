from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:123@localhost:5432/autodb"
print(DATABASE_URL)
print(list(DATABASE_URL.encode('utf-8')))

engine = create_engine(DATABASE_URL, echo=True)
print("Engine created successfully")
