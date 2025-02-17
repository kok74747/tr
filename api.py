#ультра супер пупер переводчик текстов 18+ новелл

import google.generativeai as genai
from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import PlainTextResponse
from itertools import cycle

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
    "AIzaS...",
    "AIz...",
]

key_cycle = cycle(keys)

app = FastAPI()

async def translate_text(api_key: str, text: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash-lite-preview-02-05",
        system_instruction=prompt,
        safety_settings=safety
    )
    try:
        response = await model.generate_content_async([text])
        return response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/translate", response_class=PlainTextResponse)
async def translate(text: str = Query(...)):
    if not keys:
        raise HTTPException(status_code=500, detail="не знаю что сказать")
    api_key = next(key_cycle)
    translated_text = await translate_text(api_key, text)
    return PlainTextResponse(content=translated_text)