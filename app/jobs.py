# app/jobs.py
import threading

class JobStore:
    def __init__(self):
        self._jobs = {}
        self._lock = threading.Lock()

    def create_pending(self, job_id):
        with self._lock:
            self._jobs[job_id] = {"status":"pending", "result":None}

    def save_result(self, job_id, result):
        with self._lock:
            self._jobs[job_id] = {"status":"done", "result": result}

    def get(self, job_id):
        with self._lock:
            return self._jobs.get(job_id, {"status":"not_found", "result": None})

Job = JobStore()
