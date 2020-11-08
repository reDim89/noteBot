import logging
from src.bot.note_bot import NoteBot
from src.utils.redis_manager import RedisManager

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    bot = NoteBot(token='1373845925:AAE70o7fuhI_s4tzc5zXV-T6uK4VcqHU2CM',
                  redis_manager=RedisManager())
    bot.run(server='https://notebott.herokuapp.com/', webhook_mode=True)



