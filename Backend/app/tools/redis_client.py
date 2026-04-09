import redis, os, json

REDIS_URL = os.getenv("CELERY_METADATA_URL", "redis://redis:6379/2")

r = redis.Redis.from_url(REDIS_URL, decode_responses=True)

CANCEL_TTL = 3600


def save_task(task_id: str, data: dict):
    r.set(task_id, json.dumps(data), ex=CANCEL_TTL)


def get_task(task_id: str):
    data = r.get(task_id)
    return json.loads(data) if data else None # type: ignore


def delete_task(task_id: str):
    r.delete(task_id)