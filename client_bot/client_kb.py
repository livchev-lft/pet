from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

client_start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Мои автомобили")],
        [KeyboardButton(text="➕ Новая заявка"), KeyboardButton(text="📋 Мои заявки")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие"
)

client_add_car = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="добавить автомобиль", callback_data="add_car")],
    ]
)

