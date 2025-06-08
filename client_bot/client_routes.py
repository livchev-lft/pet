from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.dependencies import get_db
from app.db.models import Client, Car

router = APIRouter(prefix="/clients", tags=["Клиенты"])

class ClientRegister(BaseModel):
    telegram_id: int
    phone: str
    name: str
    username: str | None = None
    registration_date: datetime

class CarRegister(BaseModel):
    client_id: int
    brand: str
    model: str
    number: str
    vin: str
    year: int


@router.get("/")
def get_all_clients():
    return [{"id": 1, "name": "Иван"}]

@router.get("/by-telegram/{telegram_id}")
def get_tg(telegram_id: int, db: Session = Depends(get_db)):
    client = db.query(Client).filter_by(telegram_id=telegram_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client

@router.post("/register")
async def register_client(client_data: ClientRegister, db: Session = Depends(get_db)):
    print(client_data.model_dump())
    existing_client = db.query(Client).filter_by(telegram_id=client_data.telegram_id).first()

    if existing_client:
        raise  HTTPException(status_code=400, detail="Пользователь уже зарегестрирован")

    try:

        new_client = Client(
            telegram_id=client_data.telegram_id,
            phone=client_data.phone,
            name=client_data.name,
            username=client_data.username,
            registration_date=client_data.registration_date
        )

        db.add(new_client)
        db.commit()
        db.refresh(new_client)

        return {"status": "success", "client_id": new_client.telegram_id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при регистрации: {str(e)}")

@router.get("/mycars/{telegram_id}")
async def get_mycars(telegram_id: int, db: Session = Depends(get_db)):
    mycars = db.query(Car).filter_by(client_id=telegram_id).all()
    if not mycars:
        return {"cars": []}
    return {
        "cars": [
            {
                "brand": car.brand,
                "model": car.model,
                "number": car.number,
                "vin": car.vin,
                "year": car.year
            }
            for car in mycars
        ]
    }

@router.post("/addcar")
async def add_car(client_data: CarRegister, db: Session = Depends(get_db)):
    try:
        new_car = Car(
            client_id=client_data.client_id,
            brand=client_data.brand,
            model=client_data.model,
            number=client_data.number,
            vin=client_data.vin,
            year=client_data.year
        )
        db.add(new_car)
        db.commit()
        db.refresh(new_car)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении машины: {str(e)}")