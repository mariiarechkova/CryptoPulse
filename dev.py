import sys
print(sys.executable)

import subprocess
import signal
import platform
import asyncio
from watchfiles import awatch

EXCLUDED_PATTERNS = ('.venv', '__pycache__', '.git', '.idea', '.mypy_cache')
RESTART_DELAY = 1.2

proc = None
restart_task = None


def is_excluded(path: str) -> bool:
    return any(excl in path for excl in EXCLUDED_PATTERNS)


def start_bot():
    print("🔄 Restarting bot...")
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if platform.system() == "Windows" else 0
    return subprocess.Popen(["C:/Users/marii/PycharmProjects/CryptoPulse/.venv/Scripts/python.exe", "main.py"], creationflags=flags)


def stop_bot(p: subprocess.Popen):
    if p:
        print("⛔ Gracefully stopping old bot...")
        try:
            if platform.system() == "Windows":
                p.send_signal(signal.CTRL_BREAK_EVENT)
            else:
                p.send_signal(signal.SIGINT)
            p.wait(timeout=5)
        except Exception as e:
            print(f"⚠️ Error stopping bot: {e}")


async def debounce_restart():
    global proc
    await asyncio.sleep(RESTART_DELAY)
    stop_bot(proc)
    proc = start_bot()


async def main():
    global proc, restart_task

    proc = start_bot()

    async for changes in awatch("."):
        if any(is_excluded(str(path)) for path, _ in changes):
            continue

        print("🕒 File changes detected, restarting after delay...")

        if restart_task and not restart_task.done():
            restart_task.cancel()
            try:
                await restart_task
            except asyncio.CancelledError:
                pass

        restart_task = asyncio.create_task(debounce_restart())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Stopped by user")
        stop_bot(proc)
