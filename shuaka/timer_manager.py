"""
计时提醒管理器
- 每条签到启动一个倒计时
- 时间到后语音提醒（每人仅提醒一次）
- 后台线程 + 优先级队列
"""

import time
import heapq
import threading


class TimerManager:
    def __init__(self, remind_minutes, voice_broadcaster):
        self.remind_seconds = remind_minutes * 60
        self.voice = voice_broadcaster
        self._heap = []  # (trigger_timestamp, name, id_number, sign_time_key)
        self._reminded = set()  # 已提醒记录，防止重复
        self._lock = threading.Lock()
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._worker, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def update_remind_minutes(self, remind_minutes):
        """动态更新提醒间隔（无需重启服务）"""
        self.remind_seconds = remind_minutes * 60
        print(f"[计时] 提醒间隔已更新: {remind_minutes} 分钟")

    def add_timer(self, name, id_number):
        """添加计时器，到期后提醒一遍"""
        trigger_time = time.time() + self.remind_seconds
        # 用 name+id+timestamp 作为唯一标识
        key = f"{name}|{id_number}|{int(time.time())}"
        with self._lock:
            heapq.heappush(self._heap, (trigger_time, name, id_number, key))

    def get_active_timers(self):
        """获取当前活跃计时器"""
        with self._lock:
            now = time.time()
            return [
                {"name": name, "id_number": id_number,
                 "remaining_seconds": max(0, int(t - now))}
                for t, name, id_number, _ in self._heap
            ]

    def _worker(self):
        """每秒检查到期计时器，每人提醒一遍后移除"""
        while self._running:
            triggered = []
            now = time.time()

            with self._lock:
                while self._heap and self._heap[0][0] <= now:
                    _, name, id_number, key = heapq.heappop(self._heap)
                    if key and key not in self._reminded:
                        self._reminded.add(key)
                        triggered.append((name, id_number))

            for name, _ in triggered:
                try:
                    self.voice.remind(name)
                except Exception:
                    pass

            # 定期清理已提醒集合（超过24小时的记录）
            if len(self._reminded) > 1000:
                self._reminded.clear()

            time.sleep(1)
