from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    NAME = State()
    PHONE = State()

class AddCar(StatesGroup):
    BRAND = State()
    MODEL = State()
    NUMBER = State()
    VIN = State()
    YEAR = State()

class CreateApp(StatesGroup):
    SELECT_CAR = State()
    DESCRIPTION = State()
    DATE = State()
    PRIORITY = State()