from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from client_bot.client_kb import client_start_menu
from client_bot.client_fsm import Registration, AddCar, CreateApp
from client_bot.client_func import add_car, my_cars, is_user_registered, client_registration
import aiohttp
from datetime import datetime
from aiogram.fsm.context import FSMContext

BOT_TOKEN = "7505129541:AAHsvv0Zma9NWdxgn3PghodO0mFnRNDy4Zs"

router = Router()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@router.message(F.text == "/start")
async def start_cmd(message: Message):
    await message.answer("Привет! Это клиентский бот. Сделай выбор", reply_markup=client_start_menu)

@router.message(F.text.in_([
    "➕ Новая заявка",
    "📋 Мои заявки"
]))
async def check_user(message: Message):
    telegram_id = message.from_user.id
    registered = await is_user_registered(telegram_id)
    if registered is True:
        if F.text == "➕ Новая заявка":
            pass
        if F.text == "📋 Мои заявки":
            pass


        print('ты зареган ебать')
    else:
        await client_registration(message)

@router.message(F.contact)
async def handle_contact(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    print("HANDLE CONTACT TRIGGERED")
    await state.update_data(phone=phone_number)
    await state.set_state(Registration.PHONE)
    await message.answer(
        "Спасибо! Теперь введите ваше имя:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.NAME)


@router.message(Registration.NAME)
async def handle_name(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    username = message.from_user.username

    data = await state.get_data()
    phone = data.get("phone")
    if not data:
        print('данных нет')
        return

    name = message.text

    client_data = {
        "telegram_id": telegram_id,
        "phone": phone,
        "name": name,
        "username": username,
        "registration_date": datetime.now().isoformat()
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:8000/clients/register",
                    json=client_data
            ) as response:
                print(response.status)
                if response.status == 200:
                    await message.answer("успех")
                else:
                    error = await response.text()
                    print("Ответ сервера:", error)
                    await message.answer(f"ошибка: {error}")
    except Exception as e:
        await message.answer(f"ошибка: {str(e)}")
    finally:
        await state.clear()

@router.message(F.text == "🚗 Мои автомобили")
async def handle_my_cars(message: Message):
    print('тачки')
    telegram_id = message.from_user.id
    registered = await is_user_registered(telegram_id)
    if registered is True:
        await my_cars(telegram_id, message)
    else:
        add_car(telegram_id, message)

@router.callback_query(F.data == 'add_car')
async def add_car_callback_query(callback_query: CallbackQuery, state: FSMContext):
    telegram_id = callback_query.from_user.id
    print('telegram_id:', telegram_id)
    await state.update_data(telegram_id=telegram_id)
    await callback_query.message.answer("Введите марку машины: ")
    await state.set_state(AddCar.BRAND)
    await callback_query.answer()

@router.message(AddCar.BRAND)
async def car_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Введите модель машины: ")
    await state.set_state(AddCar.MODEL)

@router.message(AddCar.MODEL)
async def car_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите номер машины: ")
    await state.set_state(AddCar.NUMBER)

@router.message(AddCar.NUMBER)
async def car_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer("Введите вин машины: ")
    await state.set_state(AddCar.VIN)

@router.message(AddCar.VIN)
async def car_vin(message: Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await message.answer("Введите год машины: ")
    await state.set_state(AddCar.YEAR)

@router.message(AddCar.YEAR)
async def car_year(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    data = await state.get_data()
    tg_id = data.get("telegram_id")
    print("Из состояния:", data)
    print("telegram_id из сообщения:", telegram_id)
    print("telegram_id из состояния:", tg_id)
    if tg_id != telegram_id:
        print('данных нет')
        return

    client_data = {
        "client_id" : telegram_id,
        "brand" : data.get("brand"),
        "model" : data.get("model"),
        "number" : data.get("number"),
        "vin": data.get("vin"),
        "year" : int(message.text),

    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "http://localhost:8000/clients/addcar",
                    json=client_data
            ) as response:
                print(response.status)
                if response.status == 200:
                    await message.answer("успех")
                else:
                    error = await response.text()
                    print("Ответ сервера:", error)
                    await message.answer(f"ошибка: {error}")
    except Exception as e:
        await message.answer(f"ошибка: {str(e)}")
    finally:
        await state.clear()

@router.message(F.text.in_(["➕ Новая заявка"]))
async def new_app(message: Message):


async def start_bot():
    dp.include_router(router)
    await dp.start_polling(bot)