import asyncio
import datetime
import json

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor
from aiogram.utils.markdown import hlink

from aiogram import types

import phonenumbers

import logging

from aiogram.dispatcher import FSMContext

from config import TOKEN

from operations import *

from states import *

import pandas as pd

import requests

import threading


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(types.KeyboardButton("Информация о розыгрыше"))
main_menu.add(types.KeyboardButton("Зарегистрировать чек"))
main_menu.add(types.KeyboardButton("Тех. поддержка"))


@dp.message_handler(commands=['start'], state='*')
async def start(mes: types.Message, state: FSMContext):

    try:
        await state.finish()
    except:
        pass

    add_user(mes.from_user.id, mes.from_user.username)

    await mes.answer("""Здравствуйте!
Вас приветствует чат-бот Sunday Coffee.

Чтобы принять участие в розыгрыше iPhone 14 нажмите на кнопку \"Зарегистрировать чек\"""", reply_markup=main_menu)


@dp.message_handler(lambda mes: mes.text == 'Отмена', state='*')
async def start(mes: types.Message, state: FSMContext):

    try:
        await state.finish()
    except:
        pass

    await mes.answer("Главное меню", reply_markup=main_menu)


@dp.message_handler(lambda m: m.text == "Тех. поддержка")
async def tech_support(mes: types.Message):

    await mes.answer("Если у Вас есть вопросы по поводу конкурса, его правилам или других вещем связанных с конкурсом, то сообщите по номеру +7 771 742 15 00")
    await mes.answer("Если у Вас есть вопросы по боту, или какие-либо технические проблемы, то сообщите @Marlen45 или по номеру +7 700 686 20 81")


@dp.message_handler(lambda m: m.text == "Информация о розыгрыше")
async def tech_support(mes: types.Message):

    await mes.answer("""РОЗЫГРЫШ iPHONE 14
ОТ SUNDAY COFFEE😍

Мы команда Sunday Coffee хотим одарить любимых гостей ценными подарками и решили запустить грандиозный новогодний конкурс 🥳

🎁 Два новеньких iPhone 14
🎁 3 AirPods 
🎁 300 порций кофе*

Условия:
⚡️ подписываемся на наш Instagram аккаунт. Вас ждёт множество полезного и развлекательного контента и конкурсов!

💸 совершить покупку в любой кофейне сети Sunday Coffee на сумму 2000 тенге. На эту сумму у нас можно взять круассан и большую порцию кофе.

💌 регистрируем чек в Telegram чат-боте

📌 ожидаем результатов конкурса. Они будут подведены 30 декабря в прямом эфире. 

Чем больше чеков вы зарегистрируете, тем выше шансы выиграть ценные призы❤️ 

Период действия акции - с 1 по 30 декабря 2022 года. 

*300 порций кофе будут разделены между десятью победителями, каждый из которых получает сертификат на 30 порций бодрящего напитка. Использовать свой запас можно до 31 марта 2023 года.""")


@dp.message_handler(lambda m: m.text == "Зарегистрировать чек")
async def submit_name(mes: types.Message):

    await AddRecord.name.set()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(types.KeyboardButton("Отмена"))

    await mes.answer("Напишите Ваше имя ", reply_markup=k)


@dp.message_handler(state=AddRecord.name)
async def submit_phone(mes: types.Message, state: FSMContext):

    await state.update_data(name=mes.text)

    await AddRecord.phone.set()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(types.KeyboardButton("Отправить контакт", request_contact=True))
    k.add(types.KeyboardButton("Отмена"))

    await mes.answer("Напишите Ваш номер телефона или нажмите \"Отправить контакт\"", reply_markup=k)


@dp.message_handler(state=AddRecord.phone, content_types=['text', 'contact'])
async def submit_cheque_number(mes: types.Message, state: FSMContext):
    if mes.contact is not None:
        try:
            num = phonenumbers.parse(mes.contact.phone_number, "KZ")
        except:
            await mes.answer('Неверный номер или формат')
            return


        if (phonenumbers.is_valid_number(num)):

            await state.update_data(phone = mes.contact.phone_number)
        else:
            await mes.answer('Неверный номер или формат')
            return

    else:
        try:
            num = phonenumbers.parse(mes.text, "KZ")
        except:
            await mes.answer('Неверный номер или формат')
            return

        if (phonenumbers.is_valid_number(num)):

            await state.update_data(phone=mes.text)

        else:
            await mes.answer('Неверный номер или формат')
            return

    await AddRecord.cheque_number.set()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(types.KeyboardButton("Отмена"))

    await mes.answer("Отлично! Осталось совсем немного. Теперь отправьте номер чека", reply_markup=k)

    with open("check_example_number.png", 'rb') as file:

        await mes.answer_photo(file, "Пример")

    await mes.answer("Номер чека выделен красным.")



@dp.message_handler(state=AddRecord.cheque_number, content_types=types.ContentTypes.all())
async def submit_cheque_photo(mes: types.Message, state: FSMContext):

    if mes.content_type == 'text':

        await state.update_data(cheque_number=mes.text)

        await AddRecord.cheque_photo.set()

        await mes.answer("""И последний шаг
Отправьте фото чека.""")

        await mes.answer("Внимание! Убедитесь, что фото сделано четко, как на примере.")

        with open("check_example.jpg", 'rb') as file:

            await mes.answer_photo(file, "Пример")

    else:
        await mes.answer("Отправьте текстовое сообщение с номером чека.")


@dp.message_handler(state=AddRecord.cheque_photo, content_types=types.ContentTypes.all())
async def submit_confirm(mes: types.Message, state: FSMContext):

    if len(mes.photo) != 0:

        print(mes.photo[-1].file_id)
        await state.update_data(cheque_photo = mes.photo[-1].file_id)

    elif mes.document is not None:

        await state.update_data(cheque_photo=mes.document.file_id)

    else:
        await mes.answer("Отправьте фото или файл")
        return

    await AddRecord.confirm.set()


    data = await state.get_data()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(types.KeyboardButton("Да"))
    k.add(types.KeyboardButton("Нет"))

    await mes.answer(f"Подтвердите ваши данные:\n   Имя: {data.get('name')}\n   Номер телефона: {data.get('phone')}\n   Номер чека: {data.get('cheque_number')}", reply_markup=k)


@dp.message_handler(state=AddRecord.confirm)
async def success_submit(mes: types.Message, state: FSMContext):
    answer = mes.text

    if answer == 'Да':

        data = await state.get_data()

        add_record(**data)


        link = hlink('Инстаграм', 'https://instagram.com/sundaycoffee.kz')

        k = types.InlineKeyboardMarkup()
        k.add(types.InlineKeyboardButton("Подписать на Instagram Sunday Coffee", url='https://instagram.com/sundaycoffee.kz'))

        await mes.answer(f"""Ваш чек успешно зарегистрирован 😍

Розыгрыш состоится:
🗓️ 30 декабря
🕖 19.00 
в прямом эфире на нашей странице в {link}.

Подпишитесь на нас, чтобы узнать результаты.

Помните, чем больше чеков, тем больше шансов выиграть iPhone 14.

Желаем вам удачи!""", reply_markup=k, parse_mode="HTML")

        await mes.answer("Главное меню", reply_markup=main_menu)

    elif answer == 'Нет':

        await mes.answer('Создание заявка отменено. Вы можете оставить заявку нажав по кнопке \"Зарегестрировать чек\"', reply_markup=main_menu)

    else:

        await mes.answer("Пожалуйста выберите Да или Нет")
        return

    await state.finish()


@dp.message_handler(commands=['report'])
async def report(mes: types.Message):
    records = get_all_records()

    msg = "Зарегестрированные чеки: "

    for record in records:
        msg += f"\n     Идентификатор: {record.id}"
        msg += f"\n             Имя: {record.name}"
        msg += f"\n             Телефон: {record.phone}"
        msg += f"\n             Номер чека: {record.cheque_number}"
        msg += f"\n             Фото чека: /photo_{record.id}"
        msg += f"\n"
        msg += f"\n             Удалить чек: /delete_{record.id}"

        if len(msg) > 3900:
            await mes.answer(msg)
            msg = ""

    msg += f"\nОбщее количество чеков: {len(records)}"

    await mes.answer(msg)


@dp.message_handler(lambda mes: mes.text.startswith('/photo'))
async def cheque_photo(mes: types.Message):

    record_id = mes.text.split('_')[1]
    record = get_record(record_id)

    try:
        await mes.answer_photo(record.cheque_photo)
    except Exception as e:
        await mes.answer_document(record.cheque_photo)


@dp.message_handler(lambda mes: mes.text.startswith('/delete'))
async def delete_cheque(mes: types.Message):

    record_id = mes.text.split('_')[1]

    await DeleteRecordState.confirm.set()

    k = types.InlineKeyboardMarkup()
    k.add(types.InlineKeyboardButton('Да', callback_data=f'delete_{record_id}'), types.InlineKeyboardButton('Нет', callback_data='no'))

    msg = "Вы уверены что хотите удалить этот чек?"

    record = get_record(record_id)

    msg += f"\n     Идентификатор: {record.id}"
    msg += f"\n         Имя: {record.name}"
    msg += f"\n         Телефон: {record.phone}"
    msg += f"\n         Номер чека: {record.cheque_number}"
    msg += f"\n         Фото чека: /photo_{record.id}"

    await mes.answer(msg, reply_markup=k)


@dp.callback_query_handlers(state=DeleteRecordState.confirm)
async def delete_cheque_confirm(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('delete'):

        await state.finish()

        data = call.data.split('_')

        res = delete_record(data[1])

        await call.answer('1')

        if res == 'yes':
            await call.bot.send_message(call.from_user.id, "Чек успешно удален", reply_markup=main_menu)

        else:
            await call.bot.send_message(call.from_user.id, "Увы ошибка((( \nСообщите @Marlen45", reply_markup=main_menu)


    elif call.data == 'no':

        await state.finish()
        await call.bot.send_message(call.from_user.id, "Отмена", reply_markup=main_menu)


    else:
        await call.bot.send_message(call.from_user.id, "Выберите \"Да \" или \"Нет\"")



@dp.message_handler(commands=['report_excel'])
async def report(mes: types.Message):
    records = get_all_records()
    today = datetime.datetime.today() + datetime.timedelta(hours=6)
    today = today.date()

    t = threading.Thread(target=write_report, args=(today, records, bot, mes))

    t.start()

    t.join()

    with open(f'{today}_report.xlsx', 'rb') as file:
        await mes.answer_document(file)



def write_report(date, records, bot, mes):
    writer = pd.ExcelWriter(f'{date}_report.xlsx', engine='xlsxwriter')

    names = []
    phones = []
    cheque_numbers = []
    cheque_photos_urls = []

    for record in records:
        names.append(record.name)
        phones.append(record.phone)
        cheque_numbers.append(record.cheque_number)

        get_url = f'https://api.telegram.org/bot{TOKEN}/getFile?file_id={record.cheque_photo}'

        data = json.loads(requests.get(get_url, headers=headers).content)

        file_path = data['result']['file_path']

        photo_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'

        cheque_photos_urls.append(photo_url)

    df = pd.DataFrame({'Имя': names, 'Телефон': phones, 'Номер чека': cheque_numbers, 'URL фото': cheque_photos_urls})

    df.to_excel(writer, sheet_name='Заявки', index=False)

    writer.save()

    # with open(f'{date}_report.xlsx', 'rb') as file:
    #     loop = asyncio.new_event_loop()
    #
    #     loop.run_until_complete(bot.send_document(mes.from_user.id, file))

        # await mes.answer_document(file)

if __name__ == "__main__":
    executor.start_polling(dp)