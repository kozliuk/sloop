import asyncio
import threading
import atexit
import signal
from functools import wraps


signal.signal(signal.SIGINT, signal.SIG_DFL)


loop = asyncio.get_event_loop()

alt = None
DAEMON = True
AUTO_CLOSE = False


def get_loop():
    return loop


def call(coro):
    if alt is None:
        _initialize()
    return asyncio.run_coroutine_threadsafe(coro, get_loop())


def _initialize():
    global alt
    alt = AsyncLoopThread(loop)
    atexit.register(alt.stop)
    alt.start()


class AsyncLoopThread(threading.Thread):

    def __init__(self, a_loop):
        super().__init__(daemon=DAEMON)
        self.loop = a_loop

    @staticmethod
    async def live():
        while True:
            await asyncio.sleep(100)

    def run(self):
        print("loop started")
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.live())
        except asyncio.CancelledError:
            print("live canceled")
        print("loop finished")

    async def _astop(self):
        for task in asyncio.Task.all_tasks(loop=self.loop):
            task.cancel()

    def stop(self):
        asyncio.run_coroutine_threadsafe(self._astop(), loop=self.loop)
        self.join()
        print("loop stopped")


def _callback(x):
    global alt
    try:
        x.result()
    except asyncio.CancelledError:
        pass
    if AUTO_CLOSE:
        pending = [task for task in asyncio.Task.all_tasks(loop=loop) if not task.done()]
        if len(pending) == 1:
            asyncio.run_coroutine_threadsafe(alt._astop(), loop=loop)
            atexit.unregister(alt.stop)
            alt = None


def wrap_coro(callback=_callback):

    def inner1(f):
        @wraps(f)
        def inner2(*args, **kwargs):
            future = call(f(*args, **kwargs))
            future.add_done_callback(callback)
            return future
        return inner2
    return inner1



