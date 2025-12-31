from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import json
from typing import Dict, Any, List

from .keyboards import *
from .openai_client import OpenAIClient
from .data.books_data import BOOKS_DATABASE
from .database import get_db
from sqlalchemy.orm import Session

router = Router()
openai_client = OpenAIClient()

# Состояния для FSM
class SearchStates(StatesGroup):
    waiting_for_author = State()
    waiting_for_year = State()

# Хранение параметров поиска в памяти (в продакшене используйте Redis)
search_params: Dict[int, Dict[str, Any]] = {}

def search_books(params: Dict) -> List[Dict]:
    """Поиск книг по параметрам"""
    filtered_books = BOOKS_DATABASE.copy()
    
    # Фильтрация по жанру
    if params.get('genre'):
        filtered_books = [b for b in filtered_books if params['genre'] in b.get('tags', [])]
    
    # Фильтрация по рейтингу
    if params.get('rating'):
        if params['rating'] == '4.5':
            filtered_books = [b for b in filtered_books if b.get('rating', 0) >= 4.5]
        elif params['rating'] == '4.0':
            filtered_books = [b for b in filtered_books if b.get('rating', 0) >= 4.0]
        elif params['rating'] == '3.5':
            filtered_books = [b for b in filtered_books if b.get('rating', 0) >= 3.5]
    
    # Фильтрация по цене
    if params.get('price'):
        if params['price'] == '0_500':
            filtered_books = [b for b in filtered_books if b.get('price', 0) <= 500]
        elif params['price'] == '500_1000':
            filtered_books = [b for b in filtered_books if 500 < b.get('price', 0) <= 1000]
        elif params['price'] == '1000_2000':
            filtered_books = [b for b in filtered_books if 1000 < b.get('price', 0) <= 2000]
        elif params['price'] == '2000':
            filtered_books = [b for b in filtered_books if b.get('price', 0) > 2000]
    
    # Фильтрация по языку
    if params.get('language'):
        lang_map = {'ru': 'Русский', 'en': 'Английский', 'fr': 'Французский', 'de': 'Немецкий'}
        if params['language'] in lang_map:
            filtered_books = [b for b in filtered_books if b.get('language') == lang_map[params['language']]]
    
    # Фильтрация по автору
    if params.get('author'):
        filtered_books = [b for b in filtered_books if params['author'].lower() in b['author'].lower()]
    
    # Фильтрация по году
    if params.get('year_from'):
        filtered_books = [b for b in filtered_books if b.get('publication_year', 0) >= params['year_from']]
    if params.get('year_to'):
        filtered_books = [b for b in filtered_books if b.get('publication_year', 9999) <= params['year_to']]
    
    # Сортировка по рейтингу (по убыванию)
    filtered_books.sort(key=lambda x: x.get('rating', 0), reverse=True)
    
    return filtered_books

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    welcome_text = """
    📚 *Добро пожаловать в Книжного Консультанта!*
    
    Я помогу вам найти идеальные книги для чтения. 
    Вот что я умею:
    
    🔍 *Найти книги по критериям* - подберу книги по жанру, рейтингу, цене и другим параметрам
    ⭐ *Персональные рекомендации* - предложу книги на основе ваших предпочтений
    🔥 *Быстрый поиск* - бестселлеры, новинки, классика
    📖 *Моя библиотека* - сохраняйте понравившиеся книги
    
    Выберите действие в меню ниже:
    """
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=get_main_menu())

@router.message(F.text == "📚 Найти книги по критериям")
async def search_by_criteria(message: Message):
    """Поиск книг по критериям"""
    search_params[message.from_user.id] = {}
    await message.answer(
        "Выберите критерии для поиска книг:",
        reply_markup=get_search_criteria_menu()
    )

@router.message(F.text == "🎭 Жанр")
async def select_genre(message: Message):
    """Выбор жанра"""
    await message.answer(
        "Выберите жанр:",
        reply_markup=get_genre_keyboard()
    )

@router.message(F.text == "⭐ Рейтинг")
async def select_rating(message: Message):
    """Выбор рейтинга"""
    await message.answer(
        "Выберите минимальный рейтинг:",
        reply_markup=get_rating_keyboard()
    )

@router.message(F.text == "💰 Цена")
async def select_price(message: Message):
    """Выбор ценового диапазона"""
    await message.answer(
        "Выберите ценовой диапазон:",
        reply_markup=get_price_keyboard()
    )

@router.message(F.text == "🗣️ Язык")
async def select_language(message: Message):
    """Выбор языка"""
    await message.answer(
        "Выберите язык книги:",
        reply_markup=get_language_keyboard()
    )

@router.message(F.text == "👤 Автор")
async def select_author(message: Message, state: FSMContext):
    """Ввод автора"""
    await message.answer("Введите имя автора (или часть имени):")
    await state.set_state(SearchStates.waiting_for_author)

@router.message(SearchStates.waiting_for_author)
async def process_author(message: Message, state: FSMContext):
    """Обработка ввода автора"""
    user_id = message.from_user.id
    if user_id not in search_params:
        search_params[user_id] = {}
    
    search_params[user_id]['author'] = message.text
    await message.answer(f"Автор установлен: {message.text}")
    await state.clear()

@router.message(F.text == "📅 Год издания")
async def select_year(message: Message, state: FSMContext):
    """Ввод года издания"""
    await message.answer("Введите диапазон лет (например: 2000-2020) или один год:")
    await state.set_state(SearchStates.waiting_for_year)

@router.message(SearchStates.waiting_for_year)
async def process_year(message: Message, state: FSMContext):
    """Обработка ввода года"""
    user_id = message.from_user.id
    if user_id not in search_params:
        search_params[user_id] = {}
    
    try:
        if '-' in message.text:
            year_from, year_to = map(int, message.text.split('-'))
            search_params[user_id]['year_from'] = year_from
            search_params[user_id]['year_to'] = year_to
            await message.answer(f"Годы установлены: {year_from}-{year_to}")
        else:
            year = int(message.text)
            search_params[user_id]['year_from'] = year
            search_params[user_id]['year_to'] = year
            await message.answer(f"Год установлен: {year}")
    except ValueError:
        await message.answer("Пожалуйста, введите корректный год или диапазон лет")
        return
    
    await state.clear()

@router.message(F.text == "🔍 Начать поиск")
async def start_search(message: Message):
    """Запуск поиска по выбранным критериям"""
    user_id = message.from_user.id
    
    if user_id not in search_params or not search_params[user_id]:
        await message.answer(
            "Вы не выбрали ни одного критерия. Пожалуйста, выберите хотя бы один параметр.",
            reply_markup=get_search_criteria_menu()
        )
        return
    
    # Поиск книг
    books = search_books(search_params[user_id])
    
    if not books:
        await message.answer(
            "😕 По вашим критериям не найдено книг. Попробуйте изменить параметры поиска.",
            reply_markup=get_search_criteria_menu()
        )
        return
    
    # Сохраняем результаты поиска
    search_params[user_id]['results'] = books
    search_params[user_id]['current_page'] = 1
    
    # Отправляем первые 3 книги
    await send_books_page(message, user_id, 1)
    
    # Получаем анализ от ИИ
    analysis = await openai_client.analyze_books_recommendation(
        books[:3], 
        search_params[user_id]
    )
    
    await message.answer(f"📊 *Анализ от книжного эксперта:*\n\n{analysis}", parse_mode="Markdown")
    
    if len(books) > 3:
        await message.answer(
            f"Найдено {len(books)} книг. Показать еще?",
            reply_markup=get_pagination_keyboard(1, (len(books) + 2) // 3, user_id)
        )

@router.callback_query(F.data.startswith("page_"))
async def process_pagination(callback: CallbackQuery):
    """Обработка пагинации"""
    data = callback.data.split('_')
    user_id = int(data[1])
    page = int(data[2])
    
    if user_id in search_params and 'results' in search_params[user_id]:
        books = search_params[user_id]['results']
        total_pages = (len(books) + 2) // 3
        
        if 1 <= page <= total_pages:
            await send_books_page(callback.message, user_id, page)
            
            # Обновляем клавиатуру пагинации
            await callback.message.edit_reply_markup(
                reply_markup=get_pagination_keyboard(page, total_pages, user_id)
            )
    
    await callback.answer()

@router.message(F.text == "⭐ Персональные рекомендации")
async def personal_recommendations(message: Message):
    """Персональные рекомендации"""
    # В реальном приложении здесь бы получались предпочтения из БД
    mock_preferences = {
        "любимые жанры": ["Фэнтези", "Научная фантастика"],
        "любимые авторы": ["Джордж Оруэлл", "J.K. Rowling"],
        "предпочитаемый язык": "Русский",
        "бюджет": "до 1500 руб"
    }
    
    mock_history = [
        "1984 - Джордж Оруэлл",
        "Harry Potter and the Philosopher's Stone - J.K. Rowling",
        "Dune - Frank Herbert"
    ]
    
    recommendations = await openai_client.generate_personal_recommendation(
        mock_preferences, mock_history
    )
    
    await message.answer(
        f"🎯 *Персональные рекомендации для вас:*\n\n{recommendations}",
        parse_mode="Markdown"
    )

@router.message(F.text == "🔍 Быстрый поиск")
async def quick_search(message: Message):
    """Быстрый поиск"""
    await message.answer(
        "Выберите категорию для быстрого поиска:",
        reply_markup=get_quick_search_keyboard()
    )

@router.message(F.text == "🔥 Бестселлеры")
async def show_bestsellers(message: Message):
    """Показать бестселлеры"""
    bestsellers = sorted(BOOKS_DATABASE, key=lambda x: x.get('rating', 0), reverse=True)[:5]
    
    response = "📈 *Топ-5 бестселлеров:*\n\n"
    for i, book in enumerate(bestsellers, 1):
        response += f"{i}. *{book['title']}* - {book['author']}\n"
        response += f"   ⭐ Рейтинг: {book.get('rating', 'нет')}/5\n"
        response += f"   💰 Цена: {book['price']} {book['currency']}\n\n"
    
    await message.answer(response, parse_mode="Markdown")

@router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    """Показать справку"""
    help_text = """
    📖 *Помощь по использованию бота*
    
    *Основные функции:*
    
    🔍 *Поиск по критериям* - выберите жанр, рейтинг, цену, язык и другие параметры
    
    ⭐ *Персональные рекомендации* - бот анализирует ваши предпочтения и предлагает книги
    
    🔥 *Быстрый поиск* - бестселлеры, новинки, классика по жанрам
    
    📖 *Моя библиотека* - сохраняйте понравившиеся книги (в разработке)
    
    *Команды:*
    /start - Начало работы
    /help - Эта справка
    
    *Советы:*
    • Используйте несколько критериев для точного поиска
    • Читайте анализ от ИИ-консультанта
    • Сохраняйте понравившиеся книги
    
    По вопросам и предложениям: @your_support_username
    """
    await message.answer(help_text, parse_mode="Markdown")

@router.callback_query(F.data.startswith("genre_"))
async def process_genre_selection(callback: CallbackQuery):
    """Обработка выбора жанра"""
    genre = callback.data.replace("genre_", "")
    user_id = callback.from_user.id
    
    if user_id not in search_params:
        search_params[user_id] = {}
    
    search_params[user_id]['genre'] = genre
    await callback.message.answer(f"Выбран жанр: {genre}")
    await callback.answer()

@router.callback_query(F.data.startswith("rating_"))
async def process_rating_selection(callback: CallbackQuery):
    """Обработка выбора рейтинга"""
    rating = callback.data.replace("rating_", "")
    user_id = callback.from_user.id
    
    if user_id not in search_params:
        search_params[user_id] = {}
    
    search_params[user_id]['rating'] = rating
    await callback.message.answer(f"Выбран рейтинг: {rating}")
    await callback.answer()

@router.callback_query(F.data.startswith("price_"))
async def process_price_selection(callback: CallbackQuery):
    """Обработка выбора цены"""
    price = callback.data.replace("price_", "")
    user_id = callback.from_user.id
    
    if user_id not in search_params:
        search_params[user_id] = {}
    
    search_params[user_id]['price'] = price
    await callback.message.answer(f"Выбран ценовой диапазон: {price}")
    await callback.answer()

@router.callback_query(F.data.startswith("lang_"))
async def process_language_selection(callback: CallbackQuery):
    """Обработка выбора языка"""
    language = callback.data.replace("lang_", "")
    user_id = callback.from_user.id
    
    if user_id not in search_params:
        search_params[user_id] = {}
    
    search_params[user_id]['language'] = language
    await callback.message.answer(f"Выбран язык: {language}")
    await callback.answer()

@router.callback_query(F.data == "back_to_criteria")
async def back_to_criteria(callback: CallbackQuery):
    """Возврат к выбору критериев"""
    await callback.message.answer(
        "Выберите критерии для поиска книг:",
        reply_markup=get_search_criteria_menu()
    )
    await callback.answer()

@router.message(F.text == "↩️ Назад в меню")
async def back_to_main_menu(message: Message):
    """Возврат в главное меню"""
    await message.answer(
        "Главное меню:",
        reply_markup=get_main_menu()
    )

async def send_books_page(message: Message, user_id: int, page: int):
    """Отправка страницы с книгами"""
    books = search_params[user_id]['results']
    start_idx = (page - 1) * 3
    end_idx = start_idx + 3
    page_books = books[start_idx:end_idx]
    
    for book in page_books:
        book_text = format_book_info(book)
        await message.answer(book_text, parse_mode="HTML")

def format_book_info(book: Dict) -> str:
    """Форматирование информации о книге"""
    text = f"""
📚 <b>{book['title']}</b>
👤 <i>{book['author']}</i>

🎭 <b>Жанр:</b> {book.get('genre', 'Не указан')}
⭐ <b>Рейтинг:</b> {book.get('rating', 'Нет')}/5
💰 <b>Цена:</b> {book['price']} {book['currency']}
🗣️ <b>Язык:</b> {book.get('language', 'Не указан')}
📅 <b>Год:</b> {book.get('publication_year', 'Не указан')}
📖 <b>Страниц:</b> {book.get('pages', 'Не указано')}

📝 <b>Описание:</b> {book.get('description', 'Нет описания')}

🏷️ <b>Теги:</b> {', '.join(book.get('tags', []))}
📚 <b>Форматы:</b> {', '.join(book.get('available_formats', []))}

📖 ISBN: {book.get('isbn', 'Не указан')}
🏢 Издательство: {book.get('publisher', 'Не указано')}
"""
    return text
