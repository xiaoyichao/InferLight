from multiprocessing.queues import Empty
from multiprocessing import queues
from datetime import datetime
import time

timeout = 5000 # 0.05s

def fake_predict(batch_data):
    print(batch_data)
    time.sleep(0.1)
    return batch_data

def worker_function(task_queue, result_dict, load_fn, predict_fn):
    model_ctx = load_fn()
    while True:
        since = datetime.now()
        batch_data = []
        task_ids = []
        for _ in range(10):
            try:
                task = task_queue.get(block=True, timeout=timeout/1e6)
                batch_data.append(task['data'])
                task_ids.append(task['id'])
                if (datetime.now()-since).microseconds>timeout:
                    break
            except Empty:
                pass

        if len(batch_data)>0:
            batch_results = predict_fn(batch_data, model_ctx)
            for idx in range(len(batch_results)):
                task_queue.task_done()
                result_dict[task_ids[idx]] = batch_results[idx]
