#ультра супер пупер переводчик текстов 18+ новелл

import google.generativeai as genai
import google.api_core.exceptions
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from itertools import cycle
import logging
import asyncio

logging.basicConfig(level=logging.ERROR)

prompt = '''
Ты — опытный переводчик, специализирующийся на локализации визуальных новелл, в частности, с явным уклоном в жанр Boys' Love.  Твоя задача — переводить тексты с английского на русский язык, максимально точно передавая смысл, стиль, настроение и эмоциональную окраску оригинала, адаптируя его для русскоязычной аудитории, знакомой с BL-тематикой.

Основные принципы перевода:

* Точность и естественность: Перевод должен быть точным и легко читаться, как если бы он изначально был написан на русском языке.
* Сохранение стиля:  Необходимо сохранить оригинальный стиль автора, включая особенности речи персонажей, использование сленга, диалектов и т.д.
* Без цензуры:  Откровенные сцены и диалоги 18+ должны быть переведены без купюр, с сохранением всех грубых, вульгарных и неформальных выражений.
* Эмоциональная окраска: Перевод должен точно передавать эмоции персонажей, используя соответствующие выражения и интонации.
* Интерфейс:  Все элементы интерфейса, кнопки, описания и т.д. должны быть переведены понятно и корректно.
* Форматирование:  Сохраняй все теги форматирования (<i>, <b>, <br> и т.д.) из исходного текста.

Пример:

Английский: <i>GAHHH!! I get so FUCKING HARD just thinking about it!</i>

Перевод: <i>АААХ!! У меня ТАК, БЛЯДЬ, СТОИТ, от одной мысли об этом!</i>

В каждом запросе я буду предоставлять текст для перевода. Твой ответ должен содержать только переведенный текст, без каких-либо пояснений или комментариев.
'''

safety = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

keys = [
    "AIzaSyAzUKbVbv-BS0o_BiWPyiyMwQgn8O8l-hw",
    "AIzaSyAXXNfEjGgjdZzOCTDPWdIcfY5IIFUEerc",
    "AIzaSyAI6QgPSLoALFnXXxxeGCykG5leBv3r5Qs",
    "AIzaSyAItkUODu9Az1OMkofQ34dR8wUJtetC_4E",
    "AIzaSyBRXG8ZFbeuJZHIw7FD5p2cMgwD6UKvgus"
]

key_cycle = cycle(keys)

app = FastAPI()

async def translate_text(api_key: str, text: str, retries: int = 5) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite-preview-02-05",
        system_instruction=prompt,
        safety_settings=safety
    )

    for attempt in range(1, retries + 1):
        try:
            response = await model.generate_content_async([text])

            if not response.candidates:
                logging.error(f"Попытка {attempt}: Google API не вернул кандидатов.")
                raise HTTPException(status_code=500, detail="Сервер не вернул ответ")

            candidate = response.candidates[0]

            if candidate.finish_reason == 5:
                logging.warning(f"Попытка {attempt}: Google API остановил генерацию (finish_reason=5). Текст: {text}")
                if attempt < retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                raise HTTPException(status_code=400, detail="Перевод невозможен: текст отклонен AI")

            if not candidate.content.parts:
                logging.error(f"Попытка {attempt}: Google API не вернул текст.")
                raise HTTPException(status_code=500, detail="Google API вернул пустой ответ")

            translated_text = "".join(part.text for part in candidate.content.parts).strip()
            return translated_text

        except google.api_core.exceptions.InternalServerError as e:
            logging.error(f"Попытка {attempt}: Ошибка сервера Google API - {e}")
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
                continue
            raise HTTPException(status_code=500, detail="Google API временно недоступен")

        except Exception as e:
            logging.error(f"Попытка {attempt}: Неизвестная ошибка при переводе: {e}", exc_info=True)
            if attempt < retries:
                await asyncio.sleep(2 ** attempt)
                continue
            raise HTTPException(status_code=500, detail="Ошибка при обработке запроса")

@app.get("/", response_class=PlainTextResponse)
async def translate(text: str = Query(...)):
    if not keys:
        raise HTTPException(status_code=500, detail="не знаю что сказать")
    api_key = next(key_cycle)
    try:
        translated_text = await translate_text(api_key, text)
        return PlainTextResponse(content=translated_text)
    except Exception as e:
        logging.error("Ошибка в обработчике /translate", exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка сервера")