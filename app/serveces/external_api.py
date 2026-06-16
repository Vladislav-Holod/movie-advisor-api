from google import genai
from google.genai import types
from fastapi import HTTPException,status
from dotenv import load_dotenv
import json
import os
import asyncio

load_dotenv()
API_KEY = os.getenv('KEY_API')

_client = genai.Client(api_key=API_KEY)
_model="gemini-3.5-flash"

async def gemini_response(prompt: str)->dict:
    for attempt in range(3):
        try:
            response = await asyncio.to_thread(
                _client.models.generate_content,
                model=_model,
                contents=f"""
            Определи основную тему книжного запроса пользователя.
            Внимание поиск ввдется в openLibrle так что надо четко ставить жанр или тему 
            
            Запрос:
            {prompt}
            Верни только JSON.
            
            Поле:
            - topic

            Тема должна быть короткой и пригодной для поиска книг.
            """,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            data = json.loads(response.text)
            return data

        except Exception as e:
            print(f"Попытка {attempt + 1}: {e}")

            if attempt < 2:
                await asyncio.sleep(2)

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Gemini API unavailable"
    )
