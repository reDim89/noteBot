import redis

class RedisManager():
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host, port, db)

    def save_notion_token(self, key, value):
        self.redis.set(key, value)
        return

    def save_storage_url(self, key, value):
        self.redis.set(key, value)
        return

    def get(self, key):
        return self.redis.get(key)
