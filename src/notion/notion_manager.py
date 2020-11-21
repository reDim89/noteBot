from notion.client import NotionClient
from notion.block import PageBlock, TextBlock
from src.utils.redis_manager import RedisManager


class NotionManager(NotionClient):
    def __init__(self, token, storage):
        super().__init__(token_v2=token)
        self.storage = self.get_block(storage)

    def get_top_level_pages(self):
        super().get_top_level_pages()

    def save_item(self, item):
        block = self.storage.children.add_new(PageBlock, title=item[:10])
        block.children.add_new(TextBlock, title=item)
        return 'Item saved!'

    def get_pages(self):
        pass