from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def user_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📅 Tadbirlar")
    builder.button(text="📨 Murojaat yuborish")
    builder.button(text="👥 Kengash a'zolari")
    builder.button(text="ℹ️ Bot haqida")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)


def admin_main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📤 E'lon yuborish")
    builder.button(text="📅 Tadbir qo'shish")
    builder.button(text="📨 Murojaatlar")
    builder.button(text="🙋 Qatnashuvchilar")
    builder.button(text="👥 Foydalanuvchilar")
    builder.button(text="➕ Kengash a'zosi qo'shish")
    builder.button(text="🗑 A'zoni o'chirish")
    builder.button(text="📊 Statistika")
    builder.button(text="🔙 Foydalanuvchi menyusi")
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)


def cancel_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="❌ Bekor qilish")
    return builder.as_markup(resize_keyboard=True)


def skip_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="⏭ O'tkazib yuborish")
    builder.button(text="❌ Bekor qilish")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def contact_kb() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.button(text="📱 Raqamni yuborish", request_contact=True)
    builder.button(text="❌ Bekor qilish")
    builder.adjust(1, 1)
    return builder.as_markup(resize_keyboard=True)


def tadbir_rsvp_kb(tadbir_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Qatnashaman", callback_data=f"rsvp_{tadbir_id}")
    return builder.as_markup()
