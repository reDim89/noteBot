from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters, MessageHandler, ConversationHandler
from src.notion.notion_manager import NotionManager

class NoteBot():
    def __init__(self, token, redis_manager):
        self.redis_manager = redis_manager
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Initialize properties for conversations
        self.entry_points = [CommandHandler('start', self.start),
                             CommandHandler('set_token', self.set_token)]
        self.states = {'LOGIN': [MessageHandler(Filters.text, self.login)]}
        self.fallbacks = []

        login_conv_handler = ConversationHandler(entry_points=self.entry_points,
                                                 states=self.states,
                                                 fallbacks=self.fallbacks)
        self.dispatcher.add_handler(login_conv_handler)
        self.dispatcher.add_handler(MessageHandler(Filters.text, self.save_to_notion))
        self.updater.start_polling()

    def start(self, update, context):
        user_id = update.message.from_user.id
        user_name = update.message.from_user.username
        if self.redis_manager.find_user_by_id(user_id):
            ## context.user_data['notion_manager'] = NotionManager(self.redis_manager.get_notion_token())
            response = 'Welcome back! Just send me a message to save it to Notion'
            context.bot.send_message(chat_id=update.effective_chat.id, text=response)
            return ConversationHandler.END
        else:
            self.redis_manager.create_user(user_id, user_name)
            response = 'Welcome! Send me your Notion token to start'
            context.bot.send_message(chat_id=update.effective_chat.id, text=response)
            return 'LOGIN'

    def set_token(self, update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Send me your Notion token')
        return 'LOGIN'

    def login(self, update, context):
        token = update.message.text
        user_id = update.message.from_user.id
        self.redis_manager.save_notion_token(user_id, token)
        context.user_data['notion_manager'] = NotionManager(token)
        context.bot.send_message(chat_id=update.effective_chat.id, text='You are all set! Send me something to save it to Notion!')
        return ConversationHandler.END

    def save_to_notion(self, update, context):
        item = update.message.text
        result = context.user_data['notion_manager'].save_item(item)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=result)
