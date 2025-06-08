from zoneinfo import available_timezones

import aiohttp
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from markdown_it.rules_core import inline
from client_bot.client_kb import client_add_car

async def is_user_registered(telegram_id: int) -> bool:
    async with aiohttp.ClientSession() as session:
        check_us = f"http://localhost:8000/clients/by-telegram/{telegram_id}"
        async with session.get(check_us) as resp:
            if resp.status == 200:
                return True
            else:
                return False

async def client_registration(message: Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await message.answer(
        "Пожалуйста, отправьте свой номер телефона для регистрации:",
        reply_markup=keyboard
    )

async def my_cars(telegram_id, message: Message) -> None:
    async with aiohttp.ClientSession() as session:
        check_cars = f"http://localhost:8000/clients/mycars/{telegram_id}"
        async with session.get(check_cars) as resp:
            print(resp.status)
            if resp.status == 200:
                data = await resp.json()
                cars = data.get("cars", [])

                if not cars:
                    await message.answer("У вас пока нет добавленных автомобилей.\n\n"
                                         "Хотите добавить новый?", reply_markup=client_add_car)
                    return
                mess = "ваши авто: \n\n"
                for idx, car in enumerate(cars, 1):
                    mess += f"🚗 {idx}. {car['brand']} {car['model']} ({car['year']})\nНомер: {car['number']}\nVIN: {car['vin']}\n\n"
                await message.answer(mess)
            else:
                await message.answer("ошибка в функции my_cars")

async def check_cars(telegram_id: int, message: Message) -> None:
    async with aiohttp.ClientSession() as session:
        available_cars = f"http://localhost:8000/clients/mycars/{telegram_id}"
        print(available_cars)