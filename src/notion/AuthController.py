from notion.client import NotionClient

class AuthController():
    def __init__(self, APIToken):
        client = NotionClient(token_v2=APIToken)
        try:
            client.get_top_level_pages()
        except:
            print('Please, provide an API Key')

    def


