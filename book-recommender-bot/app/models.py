from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import datetime

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    genre = Column(String(100))
    isbn = Column(String(20), unique=True)
    publisher = Column(String(255))
    publication_year = Column(Integer)
    pages = Column(Integer)
    language = Column(String(50))
    rating = Column(Float)
    price = Column(Float)
    currency = Column(String(3), default='USD')
    description = Column(Text)
    tags = Column(JSON)  # Список тегов/ключевых слов
    available_formats = Column(JSON)  # ['paperback', 'ebook', 'audiobook']
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String(100), unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    language_code = Column(String(10))
    preferences = Column(JSON)  # Предпочтения пользователя
    search_history = Column(JSON)  # История поиска
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, default=func.now())

class SearchSession(Base):
    __tablename__ = 'search_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    search_params = Column(JSON)  # Параметры поиска
    results = Column(JSON)  # ID найденных книг
    created_at = Column(DateTime, default=func.now())

class Recommendation(Base):
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    book_id = Column(Integer, nullable=False)
    ai_analysis = Column(Text)  # Анализ от ИИ
    match_score = Column(Float)  # Оценка соответствия
    created_at = Column(DateTime, default=func.now())
