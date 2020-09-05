from notion.client import NotionClient
from notion.block import TextBlock

client = NotionClient(token_v2='4b650003a45546274908c83f2c8a3f1bef8df612f01ff4efef2571ab451d3c042827221c2a946fe645ba3c94fe8af96092e90b5dd9143bc8d74c298e7d3a09ff3396c70fce51ddafb44043cfe8c2')
# page = client.get_top_level_pages()[1]
page = client.get_block('df01d200-104b-4c0f-a226-013f2e04ba39')
new_record = page.children.add_new(TextBlock)
new_record.title = 'This is an API test'
