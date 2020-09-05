from src.utils.redisManager import RedisManager

if __name__ == '__main__':
    r = RedisManager()
    r.set('foo', 'bar')
    print(r.get('foo'))



