import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

### ==================== состояния ====================


class Diagnose(StatesGroup):
    SELECT_APP = State()
    RESULT = State()
    TASKS = State()

class RepairTask(StatesGroup):
    SELECT_APP = State()
    MECHANIC_REPORT = State()

### ==================== KEYBOARDS ====================
client_menu = ReplyKeyboardMarkup(resize_keyboard=True)
client_menu.add("➕ Добавить авто", "🚗 Мои автомобили")
client_menu.add("📝 Создать заявку", "📋 Мои заявки")

admin_menu = ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.add("📨 Все заявки", "🆕 Ожидают валидации")
admin_menu.add("⚙️ В работе", "🔧 Готово к ремонту")
admin_menu.add("📊 Отчет по запчастям", "💳 Оплаты")
admin_menu.add("🔍 По пользователю", "🔄 Статусы пользов.")

diagnostic_menu = ReplyKeyboardMarkup(resize_keyboard=True)
diagnostic_menu.add("🆕 Новые заявки", "📋 История")

mechanic_menu = ReplyKeyboardMarkup(resize_keyboard=True)
mechanic_menu.add("🆕 К работе", "📋 История")

### ==================== START HANDLER ====================
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user = await get_user(message.from_user.id)
    if not user:
        await message.answer("Добро пожаловать! Введите ваше имя:")
        await Registration.NAME.set()
    else:
        if user.role.value == 'client':
            await message.answer("Клиентское меню:", reply_markup=client_menu)
        elif user.role.value in ('admin','superadmin'):
            await message.answer("Админ-панель:", reply_markup=admin_menu)
        elif user.role.value == 'diagnostic':
            await message.answer("Меню диагностики:", reply_markup=diagnostic_menu)
        elif user.role.value == 'mechanic':
            await message.answer("Меню механика:", reply_markup=mechanic_menu)



### ==================== REGISTRATIONS HANDLERS ====================
@dp.message_handler(state=Registration.NAME)
async def process_name(message: types.Message, state: Registration):
    await state.update_data(name=message.text)
    await message.answer("Введите телефон (+7...):")
    await Registration.PHONE.set()

@dp.message_handler(state=Registration.PHONE)
async def process_phone(message: types.Message, state: Registration):
    if not validate_phone(message.text):
        return await message.answer("Неверный формат. Попробуйте +7...")
    data = await state.get_data()
    await register_client(message.from_user.id, data['name'], message.text)
    await state.finish()
    await message.answer("✅ Регистрация завершена", reply_markup=client_menu)

### ==================== CLIENT HANDLERS ====================
@dp.message_handler(lambda m: m.text == "📝 Создать заявку")
async def cmd_create_app(message: types.Message):
    cars = await get_user_cars(message.from_user.id)
    kb = InlineKeyboardMarkup()
    for car in cars:
        kb.add(InlineKeyboardButton(f"{car.brand} {car.model} ({car.number})", callback_data=f"select_car:{car.id}"))
    await message.answer("Выберите автомобиль:" , reply_markup=kb)
    await CreateApp.SELECT_CAR.set()

@dp.callback_query_handler(lambda c: c.data.startswith("select_car"), state=CreateApp.SELECT_CAR)
async def car_selected(cq: types.CallbackQuery, state: FSMContext):
    await state.update_data(car_id=int(cq.data.split(':')[1]))
    await cq.message.answer("Опишите проблему:")
    await CreateApp.DESCRIPTION.set()

@dp.message_handler(state=CreateApp.DESCRIPTION)
async def proc_descr(m: types.Message, state: FSMContext):
    await state.update_data(description=m.text)
    kb = InlineKeyboardMarkup(row_width=3)
    for p in ["HIGH","MEDIUM","LOW"]:
        kb.insert(InlineKeyboardButton(p, callback_data=f"prio:{p}"))
    await m.answer("Выберите приоритет:", reply_markup=kb)
    await CreateApp.PRIORITY.set()

@dp.callback_query_handler(lambda c: c.data.startswith("prio"), state=CreateApp.PRIORITY)
async def set_priority(cq: types.CallbackQuery, state: FSMContext):
    pr = cq.data.split(':')[1]
    await state.update_data(priority=pr)
    await cq.message.answer("Выберите дату (YYYY-MM-DD):")
    await CreateApp.DATE.set()

@dp.message_handler(state=CreateApp.DATE)
async def proc_date(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await create_application(
        client_id=m.from_user.id,
        car_id=data['car_id'],
        problem_description=data['description'],
        priority=data['priority'],
        date=datetime.strptime(m.text, "%Y-%m-%d")
    )
    await m.answer("✅ Заявка создана.", reply_markup=client_menu)
    await state.finish()

#добавить авто
@dp.message_handler(lambda m: m.text == "➕ Добавить авто")
async def cmd_add_car(message: Message):
    await message.answer("Введите марку автомобиля:")
    await AddCar.BRAND.set()

@dp.message_handler(state=AddCar.BRAND)
async def proc_brand(message: Message, state: FSMContext):
    await state.update_data(brand=message.text)
    await message.answer("Введите модель:")
    await AddCar.MODEL.set()

@dp.message_handler(state=AddCar.MODEL)
async def proc_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("Введите гос.номер автомобиля:")
    await AddCar.NUMBER.set()

@dp.message_handler(state=AddCar.NUMBER)
async def proc_number(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    await message.answer("Введите VIN автомобиля:")
    await AddCar.VIN.set()

@dp.message_handler(state=AddCar.VIN)
async def proc_vin(message: Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await message.answer("Введите год выпуска автомобиля:")
    await AddCar.YEAR.set()


@dp.message_handler(state=AddCar.YEAR)
async def proc_year(message: Message, state: FSMContext):
    #валидация года
    if not message.text.isdigit() or not (1900 < int(message.text) <= datetime.now().year + 1):
        await message.answer("❌ Некорректный год! Введите 4 цифры (например, 2015)")
        return

    data = await state.get_data()
    full_data = {
        **data,
        "year": int(message.text),
        "user_id": message.from_user.id
    }

    try:
        #отправка
        await api_add_car(full_data)  #тут надо заменить
        await message.answer("✅ Авто добавлено!", reply_markup=client_menu)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

    await state.finish()

#мои автомобили
@dp.message_handler(lambda m: m.text == "🚗 Мои автомобили")
async def cmd_my_cars(message: Message):
    user_id = message.from_user.id
    cars = await get_user_cars(user_id)  #запрос

    if not cars:
        await message.answer("У вас нет добавленных автомобилей.", reply_markup=client_menu)
        return

    for car in cars:
        text = (
            f"🚗 {car['brand']} {car['model']}\n"
            f"▸ Госномер: {car['number']}\n"
            f"▸ VIN: {car['vin']}\n"
            f"▸ Год выпуска: {car['year']}"
        )
        await message.answer(text)


#мои заявки
@dp.message_handler(lambda m: m.text == "📋 Мои заявки")
async def cmd_my_apps(message: Message):
    user_id = message.from_user.id
    apps = await get_user_applications(user_id)  # запрос

    if not apps:
        await message.answer("У вас нет активных заявок.", reply_markup=client_menu)
        return

    for app in apps:
        status = Status(app['status']).value
        text = (
            f"📋 Заявка #{app['id']}\n"
            f"▸ Статус: {status}\n"
            f"▸ Авто: {app['car']['brand']} {app['car']['model']}\n"
            f"▸ Дата: {app['date']}\n"
            f"▸ Описание: {app['description']}"
            f"▸ Диагност: {app['diagnost']['name'] if app['diagnost'] else 'не назначен'}\n"
            f"▸ Механик: {app['mechanic']['name'] if app['mechanic'] else 'не назначен'}\n"
        )
        await message.answer(text)


### ==================== ADMIN HANDLERS ====================
@dp.message_handler(lambda m: m.text == "📨 Все заявки")
async def all_apps(message: types.Message):
    apps = await get_all_applications()
    for app in apps:
        await message.answer(format_app_summary(app))

@dp.message_handler(lambda m: m.text == "🆕 Ожидают валидации")
async def pending_validation(message: types.Message):
    apps = await get_applications_by_status('NEW')
    if not apps:
        return await message.answer("Новых заявок нет.")
    for app in apps:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅ Одобрить", callback_data=f"admin_accept:{app.id}"),
            InlineKeyboardButton("❌ Отклонить", callback_data=f"admin_reject:{app.id}")
        )
        await message.answer(format_app_summary(app), reply_markup=kb)

@dp.message_handler(lambda m: m.text == "⚙️ В работе")
async def in_progress(message: types.Message):
    apps = await get_applications_by_status('DIAGNOSTIC') + await get_applications_by_status('REPAIR')
    if not apps:
        return await message.answer("Нет заявок в процессе.")
    for app in apps:
        await message.answer(format_app_summary(app))

@dp.message_handler(lambda m: m.text == "🔧 Готово к ремонту")
async def ready_to_repair(message: types.Message):
    apps = await get_applications_by_status('READY')
    if not apps:
        return await message.answer("Нечего ремонтировать.")
    for app in apps:
        await message.answer(format_app_summary(app))

@dp.message_handler(lambda m: m.text == "📊 Отчет по запчастям")
async def parts_report(message: types.Message):
    report = await get_parts_inventory_report()
    text = "📦 Отчет по запчастям:\n" + "\n".join(f"{item.name}: {item.remaining}" for item in report)
    await message.answer(text)

@dp.message_handler(lambda m: m.text == "💳 Оплаты")
async def payments_report(message: types.Message):
    payments = await get_payments_report()
    for pay in payments:
        await message.answer(f"Заявка #{pay.app_id}: {pay.amount} руб. — {pay.status}")

@dp.message_handler(lambda m: m.text == "🔄 Статусы польз.")
async def user_statuses(message: types.Message):
    await message.answer("Введите user_id или username для фильтрации:")
    await FSMContext.set_state('ADMIN_USER_FILTER')

@dp.message_handler(state='ADMIN_USER_FILTER')
async def filter_by_user(message: types.Message, state: FSMContext):
    key = message.text.strip()
    apps = await get_applications_by_user(key)
    if not apps:
        await message.answer("Заявок не найдено.")
    for app in apps:
        await message.answer(format_app_summary(app))
    await state.finish()

@dp.message_handler(lambda m: m.text == "🔍 По пользователю")
async def monitor_user(message: types.Message):
    await message.answer("Введите user_id для мониторинга статусов:")
    await FSMContext.set_state('MONITOR_USER')

@dp.message_handler(state='MONITOR_USER')
async def monitor_user_updates(message: types.Message, state: FSMContext):
    user_id = message.text.strip()
    updates = await stream_user_application_updates(user_id)
    for upd in updates:
        await message.answer(f"#{upd.app_id}: {upd.old_status} → {upd.new_status} в {upd.time}")
    await state.finish()

### ==================== DIAGNOSTIC HANDLERS ====================
@dp.message_handler(lambda m: m.text == "🆕 Новые заявки")
async def diag_new(m: types.Message):
    apps = await get_apps_by_status(["WAITING"])
    kb = InlineKeyboardMarkup()
    for app in apps:
        kb.add(InlineKeyboardButton(f"#{app.id} ({app.car.brand})", callback_data=f"diag_app:{app.id}"))
    await m.answer("Выберите заявку:", reply_markup=kb)
    await Diagnose.SELECT_APP.set()

@dp.callback_query_handler(lambda c: c.data.startswith("diag_app"), state=Diagnose.SELECT_APP)
async def diag_select(cq: types.CallbackQuery, state: FSMContext):
    app_id = int(cq.data.split(':')[1])
    await update_app_status(app_id, "DIAGNOSTIC")
    await cq.message.answer("Введите детальное заключение диагноста:")
    await state.update_data(app_id=app_id)
    await Diagnose.RESULT.set()

@dp.message_handler(state=Diagnose.RESULT)
async def diag_result(msg: types.Message, state: FSMContext):
    await state.update_data(result=msg.text)
    await msg.answer("Укажите задачи для механика (через точку с новой строки):")
    await Diagnose.TASKS.set()

@dp.message_handler(state=Diagnose.TASKS)
async def diag_tasks(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    tasks = [t.strip() for t in msg.text.split('.') if t.strip()]
    await save_diagnostic(
        application_id=data['app_id'],
        diag_id=msg.from_user.id,
        diagnostic_report=data['result'],
        tasks=tasks
    )
    await update_app_status(data['app_id'], "READY")
    await msg.answer(f"Диагностика сохранена, задач: {len(tasks)}", reply_markup=diagnostic_menu)
    await state.finish()

### ==================== MECHANIC HANDLERS ====================
@dp.message_handler(lambda m: m.text == "🆕 К работе")
async def mech_new(m: types.Message):
    apps = await get_apps_by_status(["READY"])
    kb = InlineKeyboardMarkup()
    for app in apps:
        kb.add(InlineKeyboardButton(f"#{app.id} ({app.car.brand})", callback_data=f"mech_app:{app.id}"))
    await m.answer("Список заявок к ремонту:", reply_markup=kb)
    await RepairTask.SELECT_APP.set()

@dp.callback_query_handler(lambda c: c.data.startswith("mech_app"), state=RepairTask.SELECT_APP)
async def mech_select(cq: types.CallbackQuery, state: FSMContext):
    app_id = int(cq.data.split(':')[1])
    await update_app_status(app_id, "REPAIR")
    await cq.message.answer("Введите отчёт механика по выполненным работам:")
    await state.update_data(app_id=app_id)
    await RepairTask.MECHANIC_REPORT.set()

@dp.message_handler(state=RepairTask.MECHANIC_REPORT)
async def mech_report(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await save_mechanic_report(
        application_id=data['app_id'],
        mechanic_id=msg.from_user.id,
        mechanic_report=msg.text
    )
    await update_app_status(data['app_id'], "COMPLETED")
    await msg.answer("✅ Отчёт сохранён, заявка завершена.", reply_markup=mechanic_menu)
    await state.finish()