import requests
import os
from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters, MessageHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler
from src.notion.notion_manager import NotionManager

# TODO Отрефакторить создание экземпляров классов NotionManager и RedisManager https://miro.com/app/board/o9J_km4YvHI=/
# TODO Сделать метод вывода страниц
# TODO Сделать запрос заголовка (если пустой, то будет выбираться datetime + первые X символов


class NoteBot:
    def __init__(self, token, redis_manager):
        self.token = token
        self.redis_manager = redis_manager
        self.notion_manager = None
        self.notion_storage = None
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        fallbacks = [MessageHandler(Filters.command, self.cancel)]

        # Storage conversation
        storage_entry_points = [CommandHandler('set_storage', self.set_storage)]
        storage_states = {'SAVE_STORAGE': [MessageHandler(Filters.text, self.save_storage)]}
        storage_conv_handler = ConversationHandler(entry_points=storage_entry_points,
                                                   states=storage_states,
                                                   fallbacks=fallbacks)

        # Login conversation
        login_entry_points = [CommandHandler('set_token', self.set_token)]
        login_states = {'LOGIN': [MessageHandler(Filters.text, self.login)],
                        'SET_STORAGE': [storage_conv_handler]}
        login_conv_handler = ConversationHandler(entry_points=login_entry_points,
                                                 states=login_states,
                                                 fallbacks=fallbacks)

        # Saving conversation


        # First group of handlers - conversation to set token or storage and a message handler
        self.dispatcher.add_handler(login_conv_handler, 1)
        self.dispatcher.add_handler(storage_conv_handler, 1)
        self.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command),
                                                   self.save_to_notion), 1)

        # Second group of handlers - commands
        self.dispatcher.add_handler(CommandHandler('start', self.start), 2)
        self.dispatcher.add_handler(CommandHandler('cancel', self.cancel), 2)

    def run(self, server=None, webhook_mode=False):
        """Runs a bot either in a webhook mode, or via start_polling"""
        if webhook_mode:
            port = int(os.environ.get('PORT', 5000))
            self.updater.start_webhook(listen="0.0.0.0",
                                       port=int(port),
                                       url_path=self.token)
            self.updater.bot.setWebhook(server + self.token)
        else:
            self.updater.start_polling()

    @property
    def notion_manager(self):
        return self.notion_manager

    @property.getter
    def notion_manager(self, context):
        try:
            return context.user_data['notion_manager']
        except KeyError:
            pass
        try:
            user_id = context.user_data['id']
            token = self.redis_manager.get_notion_token(user_id)
            context.user_data['notion_manager'] = NotionManager(token)
            return context.user_data['notion_manager']
        except KeyError:
            raise KeyError('User is missing')

    @property
    def notion_storage(self):
        return self.notion_storage

    @property.getter
    def notion_storage(self, context):
        try:
            return context.user_data['notion_storage']
        except KeyError:
            pass
        try:
            user_id = context.user_data['id']
            return self.redis_manager.get_storage(user_id)
        except KeyError:
            raise KeyError('User is missing')

    @staticmethod
    def start(update, context):
        """Sends instructions"""
        intro = 'Thanks for using NoteBot.'
        step_1 = '1. You will need a Notion token to start: https://miro.medium.com/max/1400/0*_0NUXhsu4n59c85_.png'
        step_2 = '2. Use /set_token command to connect your Notion account.'
        step_3 = '3. Use /set_storage command to set the page for items you will want to save.'
        step_4 = '4. After everything is set up, just send a link or a text to the bot.'
        instructions = '\n'.join((intro, step_1, step_2, step_3, step_4))
        context.bot.send_message(chat_id=update.effective_chat.id, text=instructions)

    @staticmethod
    def cancel(update, context):
        """Abort a conversation"""
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Conversation cancelled! Use commands or send a message')
        return ConversationHandler.END

    @staticmethod
    def set_token(update, context):
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

        if not self.notion_storage:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='Now use /set_storage command to set the page for saving items')
            return ConversationHandler.END

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You are all set! Send me something to save it to Notion!')
        return ConversationHandler.END

    def set_storage(self, update, context):
        """Start a conversation to set URL for saving items"""
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Send me the URL of the Notion page you want to use fpr saving items')
        return 'SAVE_STORAGE'

    def save_storage(self, update, context):
        """Create or update storage URL in Redis"""
        storage = update.message.text
        user_id = update.message.from_user.id
        if self.redis_manager.find_user_by_id(user_id):
            self.redis_manager.save_storage(user_id, storage)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text='You need to login before setting a storage')
        return ConversationHandler.END

    def get_pages(self, update, context):
        pass

    def save_to_notion(self, update, context):
        """Save received text to Notion"""
        user_id = update.message.from_user.id
        item = update.message.text

        self.notion_manager.save_item(item)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Item saved!')
