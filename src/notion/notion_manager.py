from notion.client import NotionClient
from notion.block import PageBlock, TextBlock
from src.utils.redis_manager import RedisManager


class NotionManager(NotionClient):
    def __init__(self, token):
        super().__init__(token_v2=token)
        self.storage = self.get_block('https://www.notion.so/redim89/To-Read-f2a6ab24a46b40e19f6ccdf16f7f4f34')

    def save_item(self, item):
        self.storage.children.add_new(PageBlock, title=item)

    @staticmethod
    def set_storage(user, url):
        r = RedisManager()
        r.set(user, url)