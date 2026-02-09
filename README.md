# Book Recommender Bot

> Telegram-бот, который подбирает книги под ваш вкус через AI

Опишите, что хотите почитать — бот найдёт подходящие книги из базы и даст персональные рекомендации через GPT-4o-mini.

## Что умеет

- Ищет книги по жанру, автору, году, цене, рейтингу
- Показывает бестселлеры, новинки, классику
- Анализирует подборки через AI и объясняет, почему именно эти книги
- Даёт персональные рекомендации на основе ваших предпочтений
- Удобная навигация по результатам

## Быстрый старт

**1. Скопируйте `.env.example` в `.env`:**
```bash
cp .env.example .env
```

**2. Заполните `.env`:**
```env
TELEGRAM_BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_ключ_openai
DB_PASSWORD=придумайте_пароль
```

Токены:
- Telegram — [@BotFather](https://t.me/botfather)
- OpenAI — [platform.openai.com](https://platform.openai.com)

**3. Запустите:**
```bash
docker-compose up -d --build
```

**4. Проверьте логи:**
```bash
docker-compose logs -f bot
```

## Как пользоваться

1. Напишите `/start`
2. Выберите способ поиска:
   - По фильтрам (жанр, автор, год)
   - Быстрый поиск (бестселлеры, новинки, классика)
   - Персональные рекомендации от AI
3. Получите подборку с анализом, почему эти книги вам подойдут

## Что внутри

- **PostgreSQL** — база книг
- **Redis** — кэш и сессии
- **GPT-4o-mini** — анализ и рекомендации
- **Docker** — всё в контейнерах

## Если что-то сломалось

**Смотрите логи:**
```bash
docker-compose logs bot
```

**Перезапуск:**
```bash
docker-compose restart bot
```

**Полная перезагрузка:**
```bash
docker-compose down
docker-compose up -d --build
```

## Требования

- Docker 20.10+
- Docker Compose 2.20+

## Технологии

Python 3.11, Aiogram 3.3, OpenAI GPT-4o-mini, PostgreSQL, Redis, SQLAlchemy

---

MIT License
