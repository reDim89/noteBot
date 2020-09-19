from notion.client import NotionClient
from notion.block import PageBlock, TextBlock
from src.utils.redis_manager import RedisManager


class NotionManager(NotionClient):
    def __init__(self, token):
        super().__init__(self, token)
        r = RedisManager()
        r.save_notion_token(user_id, token)
        # Тут нужно проверять, установлена ли страничка. Если да - сохранять ее в атрибут класса,
    # чтобы не дергать каждый раз redis

    def save_item(self, item):
        self.create_record()

    @staticmethod
    def set_storage(user, url):
        r = RedisManager()
        r.set(user, url)