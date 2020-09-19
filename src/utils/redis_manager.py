import redis


class RedisManager():
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host, port, db)
        self.user_id = len(self.redis.hkeys('users')) + 1

    def save_notion_token(self, value):
        self.redis.hset('users', self.user_id, 'notion_token', value)
        return

    def save_storage_url(self, key, value):
        self.redis.set(key, value)
        return

    def get(self, key):
        return self.redis.get(key)
