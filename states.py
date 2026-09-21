from aiogram.fsm.state import State, StatesGroup


class ElanState(StatesGroup):
    text = State()


class TadbirState(StatesGroup):
    nomi = State()
    sana = State()
    joy = State()
    tavsif = State()


class JavobState(StatesGroup):
    user_id = State()
    text = State()


class AzoState(StatesGroup):
    ism = State()
    lavozim = State()
    username = State()
    photo = State()


class OchirishState(StatesGroup):
    azo_id = State()


class MurojaatState(StatesGroup):
    text = State()


class RSVPState(StatesGroup):
    tadbir_id = State()
    telefon = State()
