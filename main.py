from aiogram import Bot, types, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import time
from asyncio import sleep

bot = Bot('6705094842:AAFOMtEIBfpKmeTfv62M32D8K3mYKM8TnVk')
dp = Dispatcher(bot, storage=MemoryStorage())


class Form(StatesGroup):
    wait_for_post_delay = State()
    name = State()
    photo = State()
    price = State()
    address = State()
    phone = State()
    category = State()
    description = State()



# Initialize user statistics
user_stats = {}  # key: user chat id, value: (count, last_post_time)

USER_LIMIT = 10
POST_DELAY = 5 * 60



@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    username = message.from_user.first_name

    main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    main_keyboard.add(KeyboardButton("Создать объявление"))
    main_keyboard.add(KeyboardButton("Смотреть обьявления"))
    main_keyboard.add(KeyboardButton("Создать объявление заново"))
    main_keyboard.add(KeyboardButton("Реклама"))
    main_keyboard.add(KeyboardButton("Обратная связь"))

    await bot.send_message(message.chat.id, f"Здравствуйте, {username}! Как я могу помочь Вам сегодня?",
                           reply_markup=main_keyboard)


@dp.message_handler(lambda msg: msg.text in ["Реклама", "Обратная связь", "Создать объявление заново","Создать объявление","Смотреть обьявления"], state="*")
async def universal_handler(message: types.Message, state: FSMContext):
    if message.text == "Реклама":
        await handle_advertising_button(message)
    elif message.text == "Обратная связь":
        await handle_feedback_button(message)
    elif message.text == "Создать объявление заново":
        await create_announcement(message)
    elif message.text == "Создать объявление":
        await create_announcement(message)
    elif message.text == "Смотреть обьявления":
        await handle_watch_ads_button(message)



@dp.message_handler(lambda message: message.text == "Реклама")
async def handle_advertising_button(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "📣 Для всех вопросов по рекламе обращайтесь @Tokapb174 💼\n" +
        "- - - - - - - -\n" +
        "Мы всегда рады новым возможностям и предложениям. 😊"
    )


@dp.message_handler(lambda message: message.text == "Смотреть обьявления")
async def handle_watch_ads_button(message: types.Message):
    # Создаем инлайн-кнопки с ссылками
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("АВТО", url="https://t.me/tg_market_avto"),
        InlineKeyboardButton("1000 МЕЛОЧЕЙ", url="https://t.me/tg_market_1000_melochey"),
        InlineKeyboardButton("НЕДВИЖИМОСТЬ", url="https://t.me/tg_market_nedvizhimost"),
        InlineKeyboardButton("УСЛУГИ", url="https://t.me/tg_market_yslygi")
    )

    await bot.send_message(
        message.chat.id,
        "Выберите категорию, которую хотите посмотреть",
        reply_markup=keyboard
    )



@dp.message_handler(lambda message: message.text == "Обратная связь")
async def handle_feedback_button(message: types.Message):
    await bot.send_message(
        message.chat.id,
        "📝 Если у вас есть вопросы или предложения, пожалуйста, обращайтесь 👉 @Tokapb174 ✍️\n" +
        "- - - - - - - -\n" +
        "(по всем вопросам)"
    )

@dp.message_handler(lambda message: message.text == "Создать объявление")
async def create_announcement(message: types.Message):
    user_chat_id = message.chat.id
    stats = user_stats.get(user_chat_id)

    # Проверяет ограничения пользователей перед началом нового объявления.
    if stats is not None and stats[0] >= USER_LIMIT and int(time.time()) - stats[1] < POST_DELAY:
        remaining_time = POST_DELAY - (int(time.time()) - stats[1])
        mins, sec = divmod(remaining_time + 59, 60)  # Добавляет 59 секунд для округления в большую сторону.

        reply = f"Вы уже сделали {USER_LIMIT} объявлений сегодня. " \
                f"Пожалуйста, подождите {mins} минут {sec} секунд перед созданием нового объявления."
        await bot.send_message(user_chat_id, reply)
    else:
        await bot.send_message(user_chat_id, "1⃣ Придумайте хороший заголовок \n\n(большинство пользователей обращают внимание именно на заголовок)")
        await Form.name.set()


@dp.message_handler(state=Form.name)
async def handle_announcement_title(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await bot.send_message(message.chat.id,
                           "2⃣ Добавьте одно фото")

    await Form.next()


@dp.message_handler(state=Form.photo, content_types=types.ContentType.PHOTO)
async def handle_announcement_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)

    await bot.send_message(message.chat.id, "3⃣ Стоимость (в рублях)")

    await Form.next()

@dp.message_handler(state=Form.price)
async def handle_announcement_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)

    await bot.send_message(message.chat.id, "4⃣ Для удобства покупателей, напишите где оказывается услуга ")

    await Form.next()

@dp.message_handler(state=Form.address)
async def handle_announcement_address(message: types.Message, state: FSMContext):
    if not message.text:
        await bot.send_message(message.chat.id, "Вы продолжили, не введя адрес. Пожалуйста, введите адрес или '-' если не хотите указывать.")
    else:
        await state.update_data(address=message.text)

        await bot.send_message(message.chat.id, "5⃣ Укажите телефон\n\n(если укажите номере телефона, то он будет скрыт от \nпользователей и посмотреть его можно только нажав на кнопку\n — это защитит ваш номер телефона от массового копирования)")

        await Form.phone.set()  # Измените на это

@dp.message_handler(state=Form.phone)
async def handle_announcement_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)

    await bot.send_message(message.chat.id, "6⃣ Напишите хорошее описание\n\n(чем подробнее описание, тем меньше вопросов перед заказом вам будут задавать)")



    await Form.category.set()

@dp.message_handler(state=Form.category)
async def handle_announcement_phone(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)

    await bot.send_message(message.chat.id, "напишите 1 из 4 доступных категорий \n- - - - - - -\n"
                                            "Авто\n"
                                            "Недвижимость\n"
                                            "1000 мелочей\n"
                                            "услуги")



    await Form.description.set()


@dp.message_handler(state=Form.description)
async def handle_announcement_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()



    user_chat_id = message.chat.id
    stats = user_stats.get(user_chat_id)

    # Отправляем сообщение создателю объявления
    await bot.send_photo(
        user_chat_id,
        photo=data['photo'],
        caption=f"Название: {data['name']}\n-----------\nЦена: {data['price']}\nАдрес: {data['address']}\nТелефон: {data['phone']}\nКатегория {data['category']}\nОписание: {data['description']}"

    )

    await Form.wait_for_post_delay.set()

    if stats is not None and int(time.time()) - stats[1] < POST_DELAY:
        remaining_time = POST_DELAY - (int(time.time()) - stats[1])
        await bot.send_message(user_chat_id,
                               f"Пожалуйста, подождите {int(remaining_time / 60)} минут {remaining_time % 60} секунд перед отправкой объявления.")
        await sleep(remaining_time)  # сон до истечения остатка времени

    # Отправляем сообщение в групповой чат
    await bot.send_photo(
        '-1001989592602',
        photo=data['photo'],
        caption=f"<b>Название:</b> {data['name']}\n-----------\n<b>Цена:</b> {data['price']}\n<b>Адрес:</b> {data['address']}\n"
                f"<b>Телефон:</b> {data['phone']}\n<b>Описание</b> {data['category']}\n<b>Категория:</b> {data['description']}\n-----------\n<b>Автор объявления:</b> @{message.from_user.username}\n",

        parse_mode='HTML'
    )

    if stats is None:
        user_stats[user_chat_id] = (1, int(time.time()))
    else:
        user_stats[user_chat_id] = (stats[0] + 1, int(time.time()))

    remaining_posts = USER_LIMIT - user_stats[user_chat_id][0] if user_stats[user_chat_id][0] < USER_LIMIT else 0
    await bot.send_message(user_chat_id, f'Вы всё еще можете опубликовать {remaining_posts} объявлений сегодня.')

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp)