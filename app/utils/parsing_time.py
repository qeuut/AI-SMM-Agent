import json
from datetime import datetime
from zoneinfo import ZoneInfo

from openai import AsyncOpenAI

from AI_SMM_AGENT.app.config.settings import settings


client = AsyncOpenAI(
    api_key=settings.PROXY_API_KEY,
    base_url="https://api.proxyapi.ru/openai/v1"
)


async def parse_schedule_time(user_text: str) -> dict:
    now_dt = datetime.now(ZoneInfo("Europe/Moscow"))

    now_str = now_dt.strftime("%Y-%m-%d %H:%M:%S")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"""
                Ты парсер даты и времени.
                
                Текущее время:
                {now_str}
                
                Timezone: Europe/Moscow.
                
                Ты ОБЯЗАН:
                - понимать относительное время
                - "через 1 минуту"
                - "через 200 секунд"
                - "через час"
                - "через пятнадцать часов"
                - "завтра в 15"
                - "послезавтра"
                - "в пятницу"
                - "в пятницу следующей недели"
                - "01.06 в 14:30"
                
                Верни ТОЛЬКО JSON.
                
                Если время понятно:
                
                {{
                  "datetime": "YYYY-MM-DD HH:MM:SS"
                }}
                
                Если недостаточно данных:
                
                {{
                  "datetime": null,
                  "question": "уточняющий вопрос"
                }}
                """
            },
            {
                "role": "user",
                "content": user_text
            }
        ]
    )

    raw = response.choices[0].message.content

    return json.loads(raw)