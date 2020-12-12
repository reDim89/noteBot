from notion.client import NotionClient
from notion.block import PageBlock, TextBlock
from src.utils.redis_manager import RedisManager


class NotionManager(NotionClient):
    def __init__(self, token):
        super().__init__(token_v2=token)

    def get_pages(self):
        pages = super().get_top_level_pages()
        titles_urls = [page.title + ': ' + page.get_browseable_url()
                             for page in filter(lambda x: hasattr(x, 'title'), pages)]
        response = '\n'.join(item for item in titles_urls)
        return response

    def save_item(self, item, storage):
        storage_object = self.get_block(storage)
        block = storage_object.children.add_new(PageBlock, title=item[:50])
        block.children.add_new(TextBlock, title=item)
        return 'Item saved!'