import requests
from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters, MessageHandler, ConversationHandler
from src.notion.notion_manager import NotionManager

# TODO 1. Развернуть бота в Digital Ocean
# TODO 2. Сделать сохранение в тело заметки, а не в тайтл

class NoteBot():
    def __init__(self, token, redis_manager):
        self.redis_manager = redis_manager
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Login conversation
        self.entry_points = [CommandHandler('set_token', self.set_token)]
        self.states = {'LOGIN': [MessageHandler(Filters.text, self.login)]}
        self.fallbacks = [MessageHandler(Filters.command, self.cancel)]
        login_conv_handler = ConversationHandler(entry_points=self.entry_points,
                                                 states=self.states,
                                                 fallbacks=self.fallbacks)

        # First group of handlers - conversation to set token and a message handler
        self.dispatcher.add_handler(login_conv_handler, 1)
        self.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command),
                                                   self.save_to_notion), 1)

        # Second group of handlers - commands
        self.dispatcher.add_handler(CommandHandler('start', self.start), 2)
        self.dispatcher.add_handler(CommandHandler('get_pages', self.get_pages), 2)

        self.updater.start_polling()

    def start(self, update, context):
        """Sends instructions"""
        instructions = 'blabla'
        context.bot.send_message(chat_id=update.effective_chat.id, text=instructions)

    def cancel(self, update, context):
        """Abort a conversation"""
        context.bot.send_message('Conversation cancelled! Use commands or send a message')
        return ConversationHandler.END

    def set_token(self, update, context):
        """Start a conversation to login into notion"""
        context.bot.send_message(chat_id=update.effective_chat.id, text='Send me your Notion token')
        return 'LOGIN'

    def login(self, update, context):
        """Create or update Notion login in Redis"""
        token = update.message.text
        user_id = update.message.from_user.id
        user_name = update.message.from_user.username
        if self.redis_manager.find_user_by_id(user_id):
            self.redis_manager.save_notion_token(user_id, token)
        else:
            self.redis_manager.create_user(user_id, user_name)
            self.redis_manager.save_notion_token(user_id, token)

        context.user_data['notion_manager'] = NotionManager(token)
        context.bot.send_message(chat_id=update.effective_chat.id, text='You are all set! Send me something to save it to Notion!')
        return ConversationHandler.END

    def save_to_notion(self, update, context):
        """Save received text to Notion"""
        user_id = update.message.from_user.id
        item = update.message.text

        if 'notion_manager' in context.user_data.keys():
            context.user_data['notion_manager'].save_item(item)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Item saved!')

        elif self.redis_manager.find_user_by_id(user_id) & bool(self.redis_manager.get_notion_token(user_id)):
           token = self.redis_manager.get_notion_token(user_id).decode('UTF-8')

           try:
            context.user_data['notion_manager'] = NotionManager(token)
            context.user_data['notion_manager'].save_item(item)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Item saved!')

           except requests.HTTPError as error:
               context.bot.send_message(chat_id=update.effective_chat.id,
                                        text=str(error))
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Oooops! Looks like you need to set your token')


    def get_pages(self, update, context):
        context.user_data['notion_manager'].get_top_level_pages()
