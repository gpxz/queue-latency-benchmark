import time

import dramatiq
from dramatiq.results import Results as DramatiqResults
from dramatiq.results.backends import RedisBackend as DramatiqRedisBackend
from dramatiq.brokers.redis import RedisBroker as DramatiqRedisBroker
from dramatiq.brokers.rabbitmq import RabbitmqBroker as DramatiqRabbitmqBroker
from huey import RedisHuey
from celery import Celery

REDIS_HOST = 'redis'
REDIS_URL = f'redis://{REDIS_HOST}:6379'
RMQ_URL = 'amqp://user:password@rabbitmq:5672/'
RMQ_URL_CELERY = 'pyamqp://user:password@rabbitmq:5672/'

huey = RedisHuey(host=REDIS_HOST)

celery_redis_app = Celery('default', broker=REDIS_URL, backend=REDIS_URL)

celery_rmq_app = Celery('default', broker=RMQ_URL_CELERY, backend=REDIS_URL)


dramatiq_broker_redis = DramatiqRedisBroker(host=REDIS_HOST)
dramatiq_backend_redis = DramatiqRedisBackend(url=REDIS_URL)
dramatiq_broker_redis.add_middleware(DramatiqResults(backend=dramatiq_backend_redis))

dramatiq_broker_rmq = DramatiqRabbitmqBroker(url=RMQ_URL)
dramatiq_backend_rmq = DramatiqRedisBackend(url=REDIS_URL, namespace='dramatiq-results-rmq')
dramatiq_broker_rmq.add_middleware(DramatiqResults(backend=dramatiq_backend_rmq))


def tracked_sleep():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result

@huey.task()
def tracked_sleep_huey():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result


@dramatiq.actor(store_results=True, broker=dramatiq_broker_redis)
def tracked_sleep_dramatiq_redis():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result

@dramatiq.actor(store_results=True, broker=dramatiq_broker_rmq)
def tracked_sleep_dramatiq_rmq():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result

@celery_redis_app.task
def tracked_sleep_celery_redis():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result

@celery_rmq_app.task
def tracked_sleep_celery_rmq():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result


