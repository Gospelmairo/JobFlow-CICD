import redis
import time
import os
import signal
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True,
)

running = True


def handle_shutdown(_signum, _frame):
    global running
    logger.info("Shutdown signal received, stopping worker...")
    running = False


signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def process_job(job_id):
    try:
        logger.info("Processing job %s", job_id)
        time.sleep(2)
        r.hset(f"job:{job_id}", "status", "completed")
        logger.info("Done: %s", job_id)
    except Exception as e:
        logger.error("Error processing job %s: %s", job_id, e)
        try:
            r.hset(f"job:{job_id}", "status", "failed")
        except Exception:
            pass


while running:
    job = r.brpop("job", timeout=5)
    if job:
        _, job_id = job
        process_job(job_id)

sys.exit(0)
