"""
40分钟计时提醒管理器
- 每有一条新签到，启动一个40分钟倒计时
- 时间到后触发语音提醒
- 后台线程 + 优先级队列实现
"""

import time
import heapq
import threading


class TimerManager:
    def __init__(self, remind_minutes, voice_broadcaster):
        self.remind_seconds = remind_minutes * 60
        self.voice = voice_broadcaster
        self._heap = []  # (trigger_timestamp, name, id_number)
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def add_timer(self, name, id_number):
        """添加一个40分钟计时器"""
        trigger_time = time.time() + self.remind_seconds
        with self._lock:
            heapq.heappush(self._heap, (trigger_time, name, id_number))

    def get_active_timers(self):
        """获取当前活跃的计时器列表"""
        with self._lock:
            now = time.time()
            return [
                {"name": name, "id_number": id_number,
                 "remaining_seconds": max(0, int(t - now))}
                for t, name, id_number in self._heap
            ]

    def _worker(self):
        """后台检查线程，每秒检查一次是否有到期的计时器"""
        while self._running:
            triggered = []
            now = time.time()

            with self._lock:
                while self._heap and self._heap[0][0] <= now:
                    triggered.append(heapq.heappop(self._heap))

            for _, name, _ in triggered:
                try:
                    self.voice.remind(name)
                except Exception:
                    pass

            time.sleep(1)
