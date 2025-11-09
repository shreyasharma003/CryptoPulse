import redis

def test_redis():
    try:
        client = redis.Redis(host="localhost", port=6379, decode_responses=True)

        client.set("test_key", "Hello from Windows!")
        value = client.get("test_key")

        print("Connected to Redis!")
        print("test_key =", value)

    except Exception as e:
        print("Could not connect to Redis:", e)

if __name__ == "__main__":
    test_redis()