import threading
import time
import collections
from utils.capture_window import get_client_rect, capture_window


class FrameBuffer(threading.Thread):
    def __init__(self, threadID, name, maxlen=4):
        super().__init__()

        self.threadID = threadID
        self.name = name

        self.buffer = collections.deque(maxlen=maxlen)
        self.lock = threading.Lock()
        self.monitor = get_client_rect("Hollow Knight")

        self._stop_event = threading.Event()

    def get_frame(self):
        self.lock.acquire(blocking=True)

        img = capture_window(self.monitor)
        self.buffer.append(img)
        
        self.lock.release()

    def run(self):
        while not self.stopped():
            self.get_frame()
            time.sleep(0.05)

        # self.lock.acquire(blocking=True)
        # self.buffer.clear()
        # self.lock.release()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    
    def get_buffer(self):
        stations = []
        self.lock.acquire(blocking=True)

        for f in self.buffer:
            stations.append(f)

        self.lock.release()

        return stations

    
    