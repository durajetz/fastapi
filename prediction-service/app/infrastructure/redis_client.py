from loguru import logger
import redis

class RedisClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(host=self.host, port=self.port, decode_responses=True)
            if self.client.ping():
                logger.info(f"Connected to Redis at {self.host}:{self.port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis at {self.host}:{self.port} - {e}")

    def set(self, key: str, value: str):
        try:
            self.client.set(key, value)
            logger.info(f"Set key: {key} with value: {value} in Redis")
        except Exception as e:
            logger.error(f"Error setting key: {key} in Redis - {e}")

    def get(self, key: str):
        try:
            value = self.client.get(key)
            if value is not None:
                logger.info(f"Retrieved key: {key} with value: {value} from Redis")
            else:
                logger.warning(f"Key: {key} does not exist in Redis")
            return value
        except Exception as e:
            logger.error(f"Error retrieving key: {key} from Redis - {e}")
            return None

    def exists(self, key: str):
        try:
            exists = self.client.exists(key)
            if exists:
                logger.info(f"Key: {key} exists in Redis")
            else:
                logger.warning(f"Key: {key} does not exist in Redis")
            return exists
        except Exception as e:
            logger.error(f"Error checking if key: {key} exists in Redis - {e}")
            return False
