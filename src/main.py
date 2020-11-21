import logging
import os
from src.bot.note_bot import NoteBot
from src.utils.redis_manager import RedisManager

if __name__ == '__main__':
    if os.environ.get('notebot_debug') == '1':
        logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        bot = NoteBot(token=os.environ.get('TG_TOKEN'),
                      redis_manager=RedisManager(debug=True))
        bot.run()
    else:
        bot = NoteBot(token=os.environ.get('TG_TOKEN'),
                      redis_manager=RedisManager())
        bot.run(server='https://notebott.herokuapp.com/', webhook_mode=True)



