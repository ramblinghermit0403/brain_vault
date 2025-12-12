import redis
try:
    r = redis.from_url("redis://localhost:6379/0")
    print("Redis connection OK")
    r.set("test", "value")
    print("Redis write OK")
except Exception as e:
    print(f"Redis Error: {e}")
