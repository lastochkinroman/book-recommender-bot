import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.client = openai.OpenAI(api_key=self.api_key)
    
    async def analyze_books_recommendation(self, books: List[Dict], user_params: Dict) -> str:
        """Анализ книг и предоставление рекомендаций"""
        
        books_info = "\n".join([
            f"- '{b['title']}' by {b['author']}: "
            f"Жанр: {b.get('genre', 'не указан')}, "
            f"Рейтинг: {b.get('rating', 'нет')}/5, "
            f"Год: {b.get('publication_year', 'не указан')}, "
            f"Описание: {b.get('description', 'Нет описания')[:200]}..."
            for b in books
        ])
        
        prompt = f"""
        Ты эксперт по литературе и книжный консультант с 15-летним опытом работы.
        Проанализируй следующие книги и дай персональные рекомендации пользователю.
        
        Критерии пользователя: {user_params}
        
        Найденные книги:
        {books_info}
        
        Дай анализ по следующим аспектам:
        1. Какие книги наиболее соответствуют запросу пользователя и почему?
        2. Какие из этих книг являются must-read в своих жанрах?
        3. Для кого подойдет каждая из книг (целевая аудитория)?
        4. Какие альтернативные книги можно порекомендовать?
        5. Общие советы по выбору и чтению.
        
        Ответ предоставь в формате Markdown. Используй эмодзи для наглядности.
        Будь дружелюбным и мотивирующим.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты дружелюбный книжный эксперт, который помогает людям находить идеальные книги для чтения."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"⚠️ Не удалось получить анализ от ИИ. Ошибка: {str(e)}"
    
    async def generate_personal_recommendation(self, user_preferences: Dict, reading_history: List) -> str:
        """Генерация персонализированных рекомендаций на основе истории"""
        
        prompt = f"""
        На основе предпочтений пользователя и истории чтения, предложи 3-5 книг,
        которые могут понравиться пользователю.
        
        Предпочтения пользователя: {user_preferences}
        История чтения (последние 5 книг): {reading_history[-5:] if reading_history else 'нет истории'}
        
        Предоставь рекомендации в формате:
        1. Название книги и автор
        2. Краткое описание (1-2 предложения)
        3. Почему эта книга может понравиться пользователю
        
        Будь креативным и учитывай разнообразие жанров!
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Ты персональный книжный консультант, который знает вкусы пользователя."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Не удалось сгенерировать рекомендации. Попробуйте позже."
