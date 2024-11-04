import aiohttp
import re

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


class BotHH:
    """
    Класс телеграмм бота.
        - Принимает ссылку на вакансию с сайта hh.ru
        - Обрабатывает ее через нейросеть и возвращает список требований к кандидату
    """
    dp = Dispatcher()

    def __init__(self, bot_token, ai_token, ai_url, hh_url):
        self.bot_token = bot_token
        self.ai_token = ai_token
        self.ai_url = ai_url
        self.hh_url = hh_url
        self.get_message = self.dp.message()(self.get_message)
        self.command_start_handler = self.dp.message(CommandStart())(self.get_message)

    async def command_start_handler(self, message: Message):
        """
        Приветствие нового пользователя
        """
        await message.answer(f"Привет!, {html.bold(message.from_user.full_name)}! Отправь мне ссылку вакансии с hh.ru")

    async def get_message(self, message: Message):
        """
        Получает ссылку от пользователя.
        """
        await message.answer('Одну минутку...')
        try:
            url_str = str(message.text)
            pattern = r"/(\d{7,})"
            hhid = re.search(pattern, url_str).group(1)
            response = await self.fetch_vacancy_from_hh(hhid)
            await message.answer(f'{response}')
        except AttributeError:
            await message.answer('Некорректная ссылка, попробуй еще раз')
        except KeyError:
            await message.answer('Что-то пошло не так. Возможно у вас не включен VPN')

    async def fetch_vacancy_from_hh(self, hhid):
        """
        Делает запрос на api.hh.ru, получает ответ в формате json
        """
        url = self.hh_url + hhid
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return await self.request_to_ai(data)

    async def request_to_ai(self, vac_data):
        """
        Делает запрос на api.openai.com. Просит нейросеть вытащить из текста список необходимых навыков
        """
        prompt = 'Find in this message a list of skills from the requirements and description of the company and ' \
                 'answer on russian'

        req = {
            "model": "gpt-4",
            "messages": [{
                "role": "user",
                "content": f"{prompt} {vac_data}"
            }]
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + str(self.ai_token)
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.ai_url, json=req, headers=headers) as response:
                data = await response.json()
                return data['choices'][0]['message']['content']

    async def main(self):
        """
        Основная функция бота. Подставляет токен и запускает поллинг
        """
        bot = Bot(token=self.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        await self.dp.start_polling(bot)
