from aiogram.dispatcher.filters.state import State, StatesGroup


class AddRecord(StatesGroup):
    name = State()
    phone = State()
    cheque_photo = State()
    cheque_number = State()
    confirm = State()


class DeleteRecordState(StatesGroup):
    confirm = State()