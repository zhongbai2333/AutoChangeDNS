#!/usr/bin/env python3
import subprocess
import time
import datetime
from collections import deque
import platform
import shutil

from ..base_system.context import GlobalContext


class WhilePing(object):
    """跨平台实时监控丢包率"""

    def __init__(self):
        self._logger = GlobalContext.get_logger()

    def ping_once(self, host: str, timeout: float = 1.0) -> bool:
        """
        跨平台 ping 一次：Windows 用 '/w' (毫秒)，其他平台用 '-W' (秒)
        """
        system = platform.system().lower()
        ping_exe = shutil.which("ping")
        if not ping_exe:
            raise RuntimeError("未找到 ping 命令")

        if system == "windows":
            # Windows: -n 1 次, /w 超时(毫秒)
            timeout_ms = int(timeout * 1000)
            cmd = [ping_exe, "-n", "1", "-w", str(timeout_ms), host]
        else:
            # Linux/macOS: -c 1 次, -W 超时(秒)
            cmd = [ping_exe, "-c", "1", "-W", str(int(timeout)), host]

        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0

    def ping_loss_rate(
        self, host: str, interval: float = 1.0, window: int = 60
    ) -> float:
        """
        在给定窗口内执行连续 ping，并返回该窗口期的丢包率。
        interval: 每次 ping 间隔（秒）
        window: 滑动窗口长度（秒），脚本会在该窗口内循环发送 ping 并统计。
        """
        count = 0
        lost = 0
        end_time = time.time() + window

        while time.time() < end_time:
            ok = self.ping_once(host, timeout=interval)
            count += 1
            if not ok:
                lost += 1
            time.sleep(interval)

        loss_rate = (lost / count * 100) if count > 0 else 0.0
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._logger.info(
            f"[{ts}] {window}s 窗口: 共发 {count} 包，丢 {lost} 包，丢包率 {loss_rate:.2f}%"
        )
        return loss_rate

    def monitor_loss(self, host: str, interval: float = 1.0, window: int = 60):
        """
        实时监控丢包率：每隔 window 秒调用 ping_loss_rate 并输出。
        """
        self._logger.info(f"开始监控 {host}，每 {window}s 输出一次丢包率...")
        try:
            while True:
                _ = self.ping_loss_rate(host, interval, window)
        except KeyboardInterrupt:
            self._logger.warning("监控已停止。")
