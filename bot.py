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

    await mes.answer("Если у Вас есть вопросы по поводу конкурса, его правилам или других вещем связанных с конкурсом, то сообщите по номеру 8-800-535-35-35")
    await mes.answer("Если у Вас есть вопросы по боту, или какие-либо технические проблемы, то сообщите @Marlen45")


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
    today = datetime.datetime.today().date()
    logging.info(datetime.datetime.today())

    t = threading.Thread(target=write_report, args=(today, records))

    t.start()

    t.join()

    with open(f'{today}_report.xlsx', 'rb') as file:
        await mes.answer_document(file)


def write_report(date, records):
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

if __name__ == "__main__":
    executor.start_polling(dp)