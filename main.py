import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv

from bot import BotHH

AI_URL = 'https://api.openai.com/v1/chat/completions'
HH_URL = 'https://api.hh.ru/vacancies/'

if __name__ == "__main__":
    load_dotenv()
    bot_hh = BotHH(
        bot_token=getenv("BOT_TOKEN"),
        ai_token=getenv("AI_TOKEN"),
        ai_url=AI_URL,
        hh_url=HH_URL
    )
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(bot_hh.main())
