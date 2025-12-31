from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu():
    """Главное меню"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📚 Найти книги по критериям"))
    builder.add(KeyboardButton(text="⭐ Персональные рекомендации"))
    builder.add(KeyboardButton(text="🔍 Быстрый поиск"))
    builder.add(KeyboardButton(text="📖 Моя библиотека"))
    builder.add(KeyboardButton(text="❓ Помощь"))
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_search_criteria_menu():
    """Меню критериев поиска"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🎭 Жанр"))
    builder.add(KeyboardButton(text="👤 Автор"))
    builder.add(KeyboardButton(text="⭐ Рейтинг"))
    builder.add(KeyboardButton(text="💰 Цена"))
    builder.add(KeyboardButton(text="🗣️ Язык"))
    builder.add(KeyboardButton(text="📅 Год издания"))
    builder.add(KeyboardButton(text="🔍 Начать поиск"))
    builder.add(KeyboardButton(text="↩️ Назад в меню"))
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_genre_keyboard():
    """Клавиатура выбора жанра"""
    genres = [
        "Фэнтези", "Научная фантастика", "Детектив", "Роман",
        "Классика", "Исторический", "Биография", "Психология",
        "Поэзия", "Драма", "Приключения", "Хоррор"
    ]
    
    builder = InlineKeyboardBuilder()
    for genre in genres:
        builder.add(InlineKeyboardButton(text=genre, callback_data=f"genre_{genre}"))
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_criteria"))
    builder.adjust(3)
    return builder.as_markup()

def get_rating_keyboard():
    """Клавиатура выбора рейтинга"""
    builder = InlineKeyboardBuilder()
    ratings = [
        ("⭐ 4.5+", "rating_4.5"),
        ("⭐ 4.0+", "rating_4.0"),
        ("⭐ 3.5+", "rating_3.5"),
        ("⭐ Любой", "rating_any")
    ]
    
    for text, data in ratings:
        builder.add(InlineKeyboardButton(text=text, callback_data=data))
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_criteria"))
    builder.adjust(2)
    return builder.as_markup()

def get_price_keyboard():
    """Клавиатура выбора ценового диапазона"""
    builder = InlineKeyboardBuilder()
    prices = [
        ("💰 До 500 руб", "price_0_500"),
        ("💰 500-1000 руб", "price_500_1000"),
        ("💰 1000-2000 руб", "price_1000_2000"),
        ("💰 От 2000 руб", "price_2000"),
        ("💰 Любая", "price_any")
    ]
    
    for text, data in prices:
        builder.add(InlineKeyboardButton(text=text, callback_data=data))
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_criteria"))
    builder.adjust(2)
    return builder.as_markup()

def get_language_keyboard():
    """Клавиатура выбора языка"""
    builder = InlineKeyboardBuilder()
    languages = [
        ("🇷🇺 Русский", "lang_ru"),
        ("🇬🇧 Английский", "lang_en"),
        ("🇫🇷 Французский", "lang_fr"),
        ("🇩🇪 Немецкий", "lang_de"),
        ("🗣️ Любой", "lang_any")
    ]
    
    for text, data in languages:
        builder.add(InlineKeyboardButton(text=text, callback_data=data))
    builder.add(InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_criteria"))
    builder.adjust(2)
    return builder.as_markup()

def get_quick_search_keyboard():
    """Клавиатура быстрого поиска"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🔥 Бестселлеры"))
    builder.add(KeyboardButton(text="🎯 Новинки"))
    builder.add(KeyboardButton(text="🏆 Классика"))
    builder.add(KeyboardButton(text="📚 По жанрам"))
    builder.add(KeyboardButton(text="↩️ Назад в меню"))
    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

def get_pagination_keyboard(current_page: int, total_pages: int, search_id: int):
    """Клавиатура пагинации"""
    builder = InlineKeyboardBuilder()
    
    if current_page > 1:
        builder.add(InlineKeyboardButton(text="◀️ Назад", callback_data=f"page_{search_id}_{current_page-1}"))
    
    builder.add(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
    
    if current_page < total_pages:
        builder.add(InlineKeyboardButton(text="Вперед ▶️", callback_data=f"page_{search_id}_{current_page+1}"))
    
    builder.adjust(3)
    return builder.as_markup()
