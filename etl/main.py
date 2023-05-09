import time
from .etl import etl_task
from schedule import run_pending

# Run the task indefinitely
while True:
    run_pending()
    time.sleep(1)
