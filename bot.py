import datetime
import json

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, executor

from aiogram import types

import phonenumbers

import logging

from aiogram.dispatcher import FSMContext

from config import TOKEN

from operations import *

from states import *

import pandas as pd

import requests


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


main_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(types.KeyboardButton("Submit application"))
main_menu.add(types.KeyboardButton("Technical support"))


@dp.message_handler(commands=['start'])
async def start(mes: types.Message):
    add_user(mes.from_user.id, mes.from_user.username)

    await mes.answer("Hello", reply_markup=main_menu)


@dp.message_handler(lambda m: m.text == "Technical support")
async def tech_support(mes: types.Message):

    await mes.answer("If You have any questions about draw rules or other questions related to it You can ask it from 8-800-5353535")
    await mes.answer("If You have some technical problems or questions about it ask it from @Marlen45")


@dp.message_handler(lambda m: m.text == "Submit application")
async def submit_name(mes: types.Message):

    await AddRecord.name.set()

    await mes.answer("Enter your name", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=AddRecord.name)
async def submit_phone(mes: types.Message, state: FSMContext):

    await state.update_data(name=mes.text)

    await AddRecord.phone.set()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    k.add(types.KeyboardButton("Send contact", request_contact=True))

    await mes.answer("Enter or send your contact phone", reply_markup=k)


@dp.message_handler(state=AddRecord.phone, content_types=['text', 'contact'])
async def submit_cheque_number(mes: types.Message, state: FSMContext):
    if mes.contact is not None:
        try:
            num = phonenumbers.parse(mes.contact.phone_number, "KZ")
        except:
            await mes.answer('Invalid number or format')
            return


        if (phonenumbers.is_valid_number(num)):

            await state.update_data(phone = mes.contact.phone_number)
        else:
            await mes.answer('Invalid number or format')
            return

    else:
        try:
            num = phonenumbers.parse(mes.text, "KZ")
        except:
            await mes.answer('Invalid number or format')
            return

        if (phonenumbers.is_valid_number(num)):

            await state.update_data(phone=mes.text)

        else:
            await mes.answer('Invalid number or format')
            return

    await AddRecord.cheque_number.set()

    await mes.answer("Enter the cheque number( what is it and how to send it you can see from instruction)", reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=AddRecord.cheque_number)
async def submit_cheque_photo(mes: types.Message, state: FSMContext):

    await state.update_data(cheque_number=mes.text)

    await AddRecord.cheque_photo.set()

    await mes.answer("Send photo or file")


@dp.message_handler(state=AddRecord.cheque_photo, content_types=['photo', 'document'])
async def submit_confirm(mes: types.Message, state: FSMContext):

    if len(mes.photo) != 0:

        print(mes.photo[-1].file_id)
        await state.update_data(cheque_photo = mes.photo[-1].file_id)

    elif mes.document is not None:

        await state.update_data(cheque_photo=mes.document.file_id)

    else:
        await mes.answer("Send photo or file")
        return

    await AddRecord.confirm.set()


    data = await state.get_data()

    k = types.ReplyKeyboardMarkup(resize_keyboard=True)

    k.add(types.KeyboardButton("Yes"))
    k.add(types.KeyboardButton("No"))

    await mes.answer(f"Do you confirm ?\nName: {data.get('name')}\nPhone: {data.get('phone')}\nCheque Number: {data.get('cheque_number')}", reply_markup=k)


@dp.message_handler(state=AddRecord.confirm)
async def success_submit(mes: types.Message, state: FSMContext):
    answer = mes.text

    if answer == 'Yes':

        data = await state.get_data()

        add_record(**data)

        await mes.answer(f"Your application is successfully accepted", reply_markup=main_menu)

    elif answer == 'No':

        k = types.ReplyKeyboardMarkup(resize_keyboard=True)
        k.add(types.KeyboardButton("Submit application"))

        await mes.answer('Ok. You can resubmit Your application', reply_markup=main_menu)

    else:

        await mes.answer("Please choose Yes or No.")
        return

    await state.finish()



@dp.message_handler(commands=['report'])
async def report(mes: types.Message):
    today = datetime.datetime.today().date()

    writer = pd.ExcelWriter(f'{today}_report.xlsx', engine='xlsxwriter')

    records = get_all_records()

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

    with open(f'{today}_report.xlsx', 'rb') as file:
        await mes.answer_document(file)

if __name__ == "__main__":
    executor.start_polling(dp)