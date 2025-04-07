import queue

def create_metrics_queue():
    """
    Returns a thread-safe FIFO queue.
    """
    return queue.Queue()
