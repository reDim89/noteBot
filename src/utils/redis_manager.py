import redis
import os


class RedisManager():
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.from_url(os.environ.get("REDIS_URL"))

    def create_user(self, user_id, user_name):
        self.redis.hset(user_id, 'login', user_name)
        return

    def find_user_by_id(self, user_id):
        return self.redis.hgetall(user_id) != {}

    def save_notion_token(self, user_id, notion_token):
        self.redis.hset(user_id, 'notion_token', notion_token)
        return

    def get_notion_token(self, user_id):
        return self.redis.hget(user_id, 'notion_token')

    def save_storage(self, user_id, storage):
        self.redis.hset(user_id, 'storage', storage)
        return

    def get_storage(self, user_id):
        return self.redis.hget(user_id, 'storage')