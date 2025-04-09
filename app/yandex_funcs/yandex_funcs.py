import json
import tempfile
from io import BytesIO
from loguru import logger
import aiohttp
import aiofiles
from pydub import AudioSegment
from app.database.models import Messages, Prompts
from config import Settings


settings = Settings()


# Конвертация аудио в WAV 16kHz LPCM
def convert_audio_to_lpcm(audio_bytes, file_format):
    try:
        audio = AudioSegment.from_file(
            BytesIO(audio_bytes), format=file_format)
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_file.name, format="wav")
        temp_file.close()
        return temp_file.name
    except Exception as e:
        logger.error(f"Ошибка конвертации аудио: {e}")
        return None


# Асинхронная транскрибация через Yandex SpeechKit
async def transcribe_audio(audio: bytes, file_format: str):
    audio_path = convert_audio_to_lpcm(audio, file_format)
    if not audio_path:
        return None

    headers = {
        "Authorization": f"Api-Key {settings.YANDEX_API_KEY}"
    }

    params = {
        "folderId": settings.FOLDER_ID,
        "lang": "ru-RU",
        "format": "lpcm",
        "sampleRateHertz": 16000
    }

    try:
        logger.info("Отправка аудио в Yandex SpeechKit")

        async with aiohttp.ClientSession() as session:
            async with aiofiles.open(audio_path, "rb") as f:
                audio_data = await f.read()

            data = aiohttp.FormData()
            data.add_field('file', audio_data,
                           filename='audio.wav', content_type='audio/wav')

            async with session.post(
                settings.YANDEX_SPEECHKIT_API_URL,
                headers=headers,
                params=params,
                data=data,
                timeout=300
            ) as response:
                response_data = await response.json()

        if "result" in response_data:
            return response_data["result"]
        else:
            logger.error(f"Ошибка транскрибации: {response_data}")
            return None

    except Exception as e:
        logger.error(f"Ошибка при вызове Yandex SpeechKit API: {e}")
        return None


# Асинхронный анализ текста через YandexGPT
async def yandex_analyze(prompt: Prompts, messages: list[Messages]):
    logger.info("Начало анализа набора сообщений.")

    api_messages = []
    for message in messages:
        if message.text:
            user = message.account.username
            chat = message.chat.chat_name

            message_data = {
                "user": user,
                "chat": chat,
                "timestamp": message.timestamp.isoformat(),
                "text": message.text
            }
            api_messages.append(json.dumps(message_data, ensure_ascii=False))

    headers = {
        "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{settings.FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "system", "text": prompt.text},
            {"role": "user", "text": f"{api_messages}"}
        ]
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                settings.YANDEX_GPT_API_URL,
                headers=headers,
                json=payload,
                timeout=300
            ) as response:
                response_data = await response.json()

        if "result" in response_data:
            logger.debug(f"Ответ от YandexGPT: {response_data}")
            analysis = response_data["result"]["alternatives"][0]["message"]["text"]
            # Преобразуем строки в числа (если нужно работать с числами)
            usage = response_data["result"]["usage"]
            tokens_input = int(usage["inputTextTokens"])
            tokens_output = int(usage["completionTokens"])
            return analysis, tokens_input, tokens_output
        else:
            logger.error(f"Ошибка анализа: {response_data}")
            return None, None, None

    except Exception as e:
        logger.error(f"Ошибка при вызове YandexGPT API: {e}")
        return None, None, None
