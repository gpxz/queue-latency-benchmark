import json
import uuid
import redis
import time


redis_client = redis.Redis(host='redis', port=6379)


class Result:
    def __init__(self, job_name):
        self.job_name = job_name

    @property
    def result_key(self):
        return f'blinq:job_result:{self.job_name}'

    def block_for_return_value(self, timeout=None):
        # Timeout in seconds.
        return_value = redis_client.brpop(self.result_key, timeout=timeout)
        if return_value is None:
            return None
        else:
            return json.loads(return_value[1])

    def push_return_value(self, return_value):
        redis_client.rpush(self.result_key, json.dumps(return_value))



def _queue_key(queue_name):
    return f'blinq:queue:{queue_name}'


def enqueue(payload=None, queue_name='default'):
    # Prepare job.
    payload = payload or {}
    job_name = str(uuid.uuid4())
    job = {'name': job_name, 'payload': payload}
    encoded_job = json.dumps(job)

    # Push job to queue.
    queue_key = _queue_key(queue_name)
    redis_client.rpush(queue_key, encoded_job)

    # Return result.
    return Result(job_name)

def tracked_sleep():
    result = {}
    result['task_started_at'] = time.time()
    time.sleep(1)
    result['task_ended_at'] = time.time()
    return result



def work(queue_name='default'):
    queue_key = _queue_key(queue_name)
    while True:
        _, encoded_job = redis_client.brpop(queue_key)
        job = json.loads(encoded_job)

        # Just do the job in this worker.
        return_value = tracked_sleep()
        result = Result(job['name'])
        result.push_return_value(return_value)




if __name__ == "__main__":
    work()



