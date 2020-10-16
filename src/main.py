from src.bot.note_bot import NoteBot
from src.utils.redis_manager import RedisManager

if __name__ == '__main__':
    bot = NoteBot(token='1373845925:AAE70o7fuhI_s4tzc5zXV-T6uK4VcqHU2CM',
                  redis_manager=RedisManager())



